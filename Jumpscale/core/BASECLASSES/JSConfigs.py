from Jumpscale import j
from .JSBase import JSBase


class JSConfigs(JSBase):
    def _init_pre(self, **kwargs):

        self._model_ = None
        if "name" in kwargs:
            self.name = kwargs["name"]

    def __init_class_post(self):

        if not hasattr(self.__class__, "_CHILDCLASS"):
            raise RuntimeError("_CHILDCLASS needs to be specified")

    @property
    def _model(self):
        if self._model_ is None:
            # self._log_debug("Get model for %s"%self.__class__._location)
            bcdb = self._bcdb_selector()
            self._model_ = bcdb.model_get_from_schema(self.__class__._CHILDCLASS._SCHEMATEXT)
        return self._model_

    def _bcdb_selector(self):
        """
        always uses the system BCDB, unless if this one implements something else
        """
        if self._parent and hasattr(self._parent, "_bcdb_selector"):
            # relevant in case the parent is JSConfigsFactory
            return self._parent._bcdb_selector()
        else:
            return j.application.bcdb_system

    def _childclass_selector(self, jsxobject, **kwargs):
        """
        allow custom implementation of which child class to use
        :return:
        """
        return self.__class__._CHILDCLASS

    def new(self, name, jsxobject=None, **kwargs):
        """
        :param name: for the CONFIG item (is a unique name for the service, client, ...)
        :param jsxobject: you can right away specify the jsxobject
        :param kwargs: the data elements which will be given to JSXObject underneith (given to constructor)
        :return: the service
        """
        if not jsxobject:
            jsxobject = self._model.new(data=kwargs)
            jsxobject.name = name
        jsconfig_klass = self._childclass_selector(jsxobject=jsxobject)
        jsconfig = jsconfig_klass(parent=self, jsxobject=jsxobject)
        jsconfig._triggers_call(jsconfig, "new")
        self._children[name] = jsconfig
        return self._children[name]

    def get(self, name="main", **kwargs):
        """
        :param name: of the object
        """
        jsconfig = self._get(name=name, die=False)
        if not jsconfig:
            self._log_debug("NEW OBJ:%s:%s" % (name, self._name))
            jsconfig = self.new(name=name)
        jsconfig._triggers_call(jsconfig, "get")
        if kwargs:
            jsconfig._data_update(kwargs)
        return jsconfig

    def exists(self, name="main"):
        """
        :param name: of the object
        """
        r = self._get(name=name, die=False)
        if r:
            return True
        return False

    def _get(self, name="main", die=True):

        if name is not None and name in self._children:
            return self._children[name]

        self._log_debug("get child:'%s' with id:%s from '%s'" % (name, id, self._name))

        # new = False

        res = self.find(name=name)

        if len(res) < 1:
            if not die:
                return
            raise RuntimeError("Did not find instance for:%s, name searched for:%s" % (self.__class__._location, name))

        elif len(res) > 1:
            raise RuntimeError(
                "Found more than 1 service for :%s, name searched for:%s" % (self.__class__._location, name)
            )
        else:
            jsxconfig = res[0]

        return jsxconfig

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
        for key, item in self._children.items():
            match = True
            for key, val in kwargs.items():
                if hasattr(item, key):
                    if val != getattr(item, key):
                        match = False
                else:
                    raise ValueError("could not find for prop:%s, did not exist in %s" % (key, self._key))
            if match:
                res.append(item)
        for jsxobject in self._findData(**kwargs):
            name = jsxobject.name
            if name in self._children:
                if jsxobject not in res:
                    raise RuntimeError("should always be there")
            else:
                r = self.new(name=name, jsxobject=jsxobject)
                res.append(r)
        return res

    def count(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the config objects
        """
        return len(self._findData(**kwargs))

    def _findData(self, **kwargs):
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
        res = self._findData(name=name)
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

    def _children_names_get(self, filter=None):
        """
        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        :param self:
        :param filter:
        :return:
        """

        def do():
            x = []
            for key, item in self._children.items():
                x.append(key)
            for item in self._findData():
                if item.name not in x:
                    x.append(item.name)
            return x

        x = self._cache.get(key="_children_names_get", method=do, expire=10)  # will redo every 10 sec
        return self._filter(filter=filter, llist=x, nameonly=True)

    def _children_get(self, filter=None):
        """
        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        :return:
        """
        x = []
        for key, item in self._children.items():
            x.append(item)
        for item in self.findData():
            if item not in x:
                x.append(item)
        return self._filter(filter=filter, llist=x, nameonly=False)

    def __getattr__(self, name):
        # if private or non child then just return
        if (
            name.startswith("_")
            or name in self._methods_names_get()
            or name in self._properties_names_get()
            or name in self._dataprops_names_get()
        ):
            return self.__getattribute__(name)  # else see if we can from the factory find the child object
        r = self._get(name=name, die=False)
        if not r:
            raise RuntimeError(
                "try to get attribute: '%s', instance did not exist, was also not a method or property, was on '%s'"
                % (name, self._key)
            )
        return r