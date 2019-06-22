from Jumpscale import j

from .JSBase import JSBase

# from .JSBaseDataObj import JSBaseDataObj


class JSBaseConfigs(JSBase):
    def __init__(self, parent=None, topclass=True, **kwargs):
        self._children = {}

        JSBase.__init__(self, parent=parent, topclass=False)

        self._model_ = None

        if topclass:
            self._init2(**kwargs)
            self._init()

    def _class_init(self):

        if not hasattr(self.__class__, "_class_init_done"):

            if not hasattr(self.__class__, "_CHILDCLASS"):
                raise RuntimeError("_CHILDCLASS needs to be specified")

            # always needs to be in this order at end
            JSBase._class_init(self)
            self.__class__.__objcat_name = "instances"

            # print("classinit:%s"%self.__class__)

    @property
    def _model(self):
        if self._model_ is None:
            # self._log_debug("Get model for %s"%self.__class__._location)
            self._model_ = j.application.bcdb_system.model_get_from_schema(self.__class__._CHILDCLASS._SCHEMATEXT)
        return self._model_

    def _childclass_selector(self, **kwargs):
        """
        allow custom implementation of which child class to use
        :return:
        """
        return self.__class__._CHILDCLASS

    def new(self, name, **kwargs):
        """
        :param name: for the service
        :param kwargs: the data elements
        :param childclass_name, if different typen of childclass, specify its name
        :return: the service
        """
        data = self._model.new(data=kwargs)
        data.name = name
        r = self._childclass_create(name=name, data=data, kwargs=kwargs)
        r._isnew = True
        return r

    def get(self, name="main", id=None, die=True, create_new=True, **kwargs):
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

        self._log_debug("get child:'%s' with id:%s from '%s'" % (name, id, self._name), data=kwargs)

        new = False
        if id:
            data = self._model.get(obj_id=id)

        elif name:
            res = self.findData(name=name)

            if len(res) < 1:
                if create_new:
                    return self.new(name=name, **kwargs)
                else:
                    if not die:
                        return
                    raise RuntimeError(
                        "Did not find instance for:%s, name searched for:%s" % (self.__class__._location, name)
                    )

            elif len(res) > 1:
                raise RuntimeError(
                    "Found more than 1 service for :%s, name searched for:%s" % (self.__class__._location, name)
                )
            else:
                data = res[0]
                if kwargs:
                    data._data_update(data=kwargs)
        else:
            if kwargs == {}:
                raise RuntimeError("kwargs need to be specified is name is not.")
            res = self.findData(**kwargs)
            if len(res) < 1:
                raise RuntimeError(
                    "Did not find instances for :%s, search criteria:\n%s" % (self.__class__._location, kwargs)
                )

            elif len(res) > 1:
                raise RuntimeError(
                    "Found more than 1 service for :%s, search criteria:\n%s" % (self.__class__._location, kwargs)
                )
            else:
                data = res[0]

        return self._childclass_create(name=name, data=data, kwargs=kwargs)

    def _childclass_create(self, name, data, kwargs):
        if name not in kwargs:
            kl = self._childclass_selector(name=name, **kwargs)
        else:
            kl = self._childclass_selector(**kwargs)
        self._children[name] = kl(data=data, parent=self, **kwargs)
        return self._children[name]

    def reset(self):
        """
        will destroy all data in the DB, be carefull
        :return:
        """
        self._log_debug("reset all data")
        for item in self.find():
            item.delete()
        self._children = {}

    def find(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the config objects
        """
        res = []
        for dataobj in self.findData(**kwargs):
            res.append(self.get(id=dataobj.id))
        return res

    def count(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the config objects
        """
        return len(self.findData(**kwargs))

    def findData(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the data objects (the data of the model)
        """

        if len(kwargs) > 0:
            propnames = [i for i in kwargs.keys()]
            propnames_keys_in_schema = [
                item.name for item in self._model.schema.properties_index_keys if item.name in propnames
            ]
            if len(propnames_keys_in_schema) > 0:
                # we can try to find this config
                return self._model.find(**kwargs)
            else:
                raise RuntimeError(
                    "cannot find obj with kwargs:\n%s\n in %s\nbecause kwargs do not match, is there * in schema"
                    % (kwargs, self)
                )
            return []
        else:
            return self._model.find()

    def delete(self, name):
        o = self.get(name)
        o.delete()

    def exists(self, name):
        res = self.findData(name=name)
        if len(res) > 1:
            raise RuntimeError("found too many items for :%s, args:\n%s\n%s" % (self.__class__.__name__, kwargs, res))
        elif len(res) == 1:
            return True
        else:
            return False

    def _obj_cache_reset(self):
        JSBase._obj_cache_reset(self)
        for key, obj in self._children.items():
            obj._obj_cache_reset()
            del self._children[key]
            self._children.pop(key)

    def _properties_children(self):
        # list the children from the factory
        if not j.data._bcdb:
            return []
        x = []
        for key, item in self._children.items():
            x.append(key)
        for item in self.findData():
            if item.name not in x:
                x.append(item.name)
        return x

    def __getattr__(self, name):
        # if private then just return
        if name.startswith("_") or name in self._methods() or name in self._properties():
            return self.__getattribute__(name)
        # else see if we can from the factory find the child object
        r = self.get(name=name, die=False, create_new=False)
        # if none means does not exist yet will have to create a new one
        if r is None:
            r = self.new(name=name)
        return r

    def __setattr__(self, key, value):
        self.__dict__[key] = value
