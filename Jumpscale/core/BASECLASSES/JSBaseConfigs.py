from Jumpscale import j

from .JSBase import JSBase

METHODS = {"find": "_Find",
           "get": "_Get",
           "reset": "_Reset",
           "count": "_Count",
           "delete": "_Delete",
           "new": "_New",
           "exists": "_Exists"}


class JSBaseConfigs(JSBase):

    def __init__(self):

        self._model_ = None
        self._children = {}

        self._class_init()  # is needed to init class properties, needs to be first thing
        JSBase.__init__(self, init=False)

        if not hasattr(self.__class__, "_CHILDCLASS"):
            raise RuntimeError("_CHILDCLASS needs to be specified")

        self._init()

    def _model_get(self):
        if self._model_ is None:
            self._model_ = j.application.bcdb_system.model_get_from_schema(self.__class__._CHILDCLASS._SCHEMATEXT)
        return self._model_

    def _childclass_selector(self):
        """
        allow custom implementation of which child class to use
        :return:
        """
        return self.__class__._CHILDCLASS

    def _New(self, name, **kwargs):
        """
        :param name: for the service
        :param kwargs: the data elements
        :param childclass_name, if different typen of childclass, specify its name
        :return: the service
        """
        kl = self._childclass_selector()
        data = self._model.new(data=kwargs)
        data.name = name
        self._children[name] = kl(factory=self, data=data)
        self._children[name]._data_trigger_new()
        self._children[name]._isnew = True
        return self._children[name]

    def _Get(self, name=None, id=None, create_new=True, **kwargs):
        """
        :param id: id of the obj to find, is a unique id
        :param name: of the object, can be empty when searching based on id or the search criteria (kwargs)
        :param search criteria (if name not used) or data elements for the new one being created
        :param die, means will give error when object not found
        :param create_new, if True it will automatically create a new one
        :param childclass_name, if different typen of childclass, specify its name, needs to be implemented in _childclass_selector
        :return: the service
        """
        if name is not None and name in self._children:
            return self._children[name]
        new = False
        if id:
            data = self._model.get(obj_id=id)

        elif name:
            res = self._FindData(name=name)
            if len(res) < 1:
                if create_new:
                    new = True
                    data = self._model.new(data=kwargs)
                    data.name = name
                else:
                    return self._error_input_raise("Did not find instance for:%s, name searched for:%s" % (self.__class__._location, name))

            elif len(res) > 1:
                return self._error_input_raise("Found more than 1 service for :%s, name searched for:%s" % (self.__class__._location, name))
            else:
                data = res[0]
        else:
            res = self._FindData(**kwargs)
            if len(res) < 1:
                if create_new:
                    data = self._model.new(data=kwargs)
                    new = True
                else:
                    return self._error_input_raise("Did not find instances for :%s, search criteria:\n%s" % (self.__class__._location, kwargs))

            elif len(res) > 1:
                return self._error_input_raise("Found more than 1 service for :%s, search criteria:\n%s" % (self.__class__._location, kwargs))
            else:
                data = res[0]

        kl = self._childclass_selector()
        self._children[name] = kl(data=data, factory=self)
        if new:
            self._children[name]._data_trigger_new()
            self._children[name]._isnew = True

        return self._children[name]

    def _Reset(self):
        """
        will destroy all data in the DB, be carefull
        :return:
        """
        for item in self._Find():
            item.delete()

    def _Find(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the config objects
        """
        res = []
        for dataobj in self._FindData(**kwargs):
            res.append(self._Get(id=dataobj.id))
        return res

    def _Count(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the config objects
        """
        return len(self._FindData(**kwargs))

    def _FindData(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the data objects (the data of the model)
        """

        if len(kwargs) > 0:
            propnames = [i for i in kwargs.keys()]
            propnames_keys_in_schema = [
                item.name for item in self._model.schema.properties_index_keys if item.name in propnames]
            if len(propnames_keys_in_schema) > 0:
                # we can try to find this config
                return self._model.get_from_keys(**kwargs)
            else:
                raise RuntimeError(
                    "cannot find obj with kwargs:\n%s\n in %s\nbecause kwargs do not match, is there * in schema" % (kwargs, self))
            return []
        else:
            return self._model.get_all()

    def _Delete(self, name):
        o = self._Get(name)
        o.delete()

    def _Exists(self, **kwargs):
        res = self._FindData(**kwargs)
        if len(res) > 1:
            raise RuntimeError("found too many items for :%s, args:\n%s\n%s" % (self.__class__.__name__, kwargs, res))
        elif len(res) == 1:
            return True
        else:
            return False

    def _obj_cache_reset(self):
        for key, obj in self._children.items():
            obj._obj_cache_reset()
            del self._children[key]
            self._children.pop(key)

    def __getattr__(self, name):
        # if private then just return
        if name == "_model":
            return self._model_get()
        if name.startswith("_"):
            return self.__getattribute__(name)
        if name.casefold() in METHODS:
            return self.__getattribute__(METHODS[name.casefold()])
        # else see if we can from the factory find the child object
        r = self._Get(name=name, die=False)
        # if none means does not exist yet will have to create a new one
        if r is None:
            r = m.new(name=name)

        return r

    def __dir__(self):
        # list the children from the factory
        x = [item.name for item in self._children.values()]
        for item in self._FindData():
            if item.name not in x:
                x.append(item.name)
        for i in METHODS.keys():
            x.append(i[0].upper()+i[1:].lower()+"(")
        return x

    def __setattr__(self, key, value):
        # if key.startswith("_"):
        #     self.__dict__[key]=value
        #     return
        self.__dict__[key] = value

    def __str__(self):
        out = "%s\n" % self.__jslocation__
        # out+="methods:\n"
        # for item in METHODS:
        #     out+=" - %s\n"%item
        # out+="instances:"
        for item in self.__dir__():
            # if item in METHODS:
            #     continue
            out += " - %s\n" % item
        return out

    __repr__ = __str__
