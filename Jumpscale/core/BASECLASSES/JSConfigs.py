from Jumpscale import j
from .JSBase import JSBase


class JSConfigs(JSBase):
    def _init_pre(self, **kwargs):
        print("JSCONFIGS:%s" % self._name)
        self._members = {}
        self._model_ = None
        self._triggers = []

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

    def _childclass_selector(self, jsxobject):
        """
        allow custom implementation of which child class to use
        :return:
        """
        return self.__class__._CHILDCLASS

    def _trigger_add(self, method):
        """

        triggers are called with (jsconfigs, jsconfig, action)

        can register any method you want to respond on some change

        - jsconfigs: the obj coming from this class, the collection of jsconfigs = jsxconfig_object
        - jsconfig: the jsconfig object
        - action: e.g. new, delete, get,stop, ...

        return: jsconfig object
        """
        if method not in self._triggers:
            self._triggers.append(method)

    def _triggers_call(self, jsconfig, action=None):
        """
        will go over all triggers and call them with arguments given

        """
        assert isinstance(jsconfig, j.application.JSConfigClass)
        for method in self._triggers:
            jsconfig = method(jsconfigs=self, jsconfig=jsconfig, action=action)
            assert isinstance(jsconfig, j.application.JSConfigClass)
        return jsconfig

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
        jsconfig_klass = self._childclass_selector(jsxobject)
        jsconfig = jsconfig_klass(parent=self, jsxobject=jsxobject)
        self._triggers_call(jsconfig, "new")
        self._members[name] = jsconfig
        return self._members[name]

    def get(self, name="main"):
        """
        :param name: of the object
        """
        jsconfig = self._get(name=name)
        jsconfig = self._triggers_call(jsconfig, "get")
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

        if name is not None and name in self._members:
            return self._members[name]

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
        self._members = {}

    def find(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the config objects
        """
        res = []
        for jsxobject in self._findData(**kwargs):
            name = jsxobject.name
            if name in self._members:
                res.append(self._members[name])
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
        res = self.findData(name=name)
        if len(res) > 1:
            raise RuntimeError("found too many items for :%s, args:\n%s\n%s" % (self.__class__.__name__, kwargs, res))
        elif len(res) == 1:
            return True
        else:
            return False

    def _obj_cache_reset(self):
        JSBase._obj_cache_reset(self)
        for key, obj in self._members.items():
            obj._obj_cache_reset()
            del self._members[key]
            self._members.pop(key)

    def _members_names_get(self, filter=None):
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
            for key, item in self._members.items():
                x.append(key)
            for item in self._findData():
                if item.name not in x:
                    x.append(item.name)
            return x

        x = self._cache.get(key="_members_names_get", method=do, expire=10)  # will redo every 10 sec
        return self._filter(filter=filter, llist=x, nameonly=True)

    def _members_get(self, filter=None):
        """
        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        :return:
        """
        x = []
        for key, item in self._members.items():
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
        # if none means does not exist yet will have to create a new one
        if r is None:
            r = self.new(name=name)
        return r

    def __setattr__(self, key, value):
        self.__dict__[key] = value
