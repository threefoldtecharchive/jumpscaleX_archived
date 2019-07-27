from Jumpscale import j
from .JSBase import JSBase

from .Attr import Attr


class JSConfigs(JSBase, Attr):
    def _init_pre(self, **kwargs):

        self._model_ = None
        if "name" in kwargs:
            self.name = kwargs["name"]

    def __init_class_post(self):

        if not hasattr(self.__class__, "_CHILDCLASS"):
            raise RuntimeError("_CHILDCLASS needs to be specified")

        if isinstance(j.application.JSBaseConfigClass) and isinstance(j.application.JSBaseConfigsClass):
            raise RuntimeError("combination not allowed of config and configsclass")

    def _process_schematext(self, schematext):
        """
        rewrites the schema in such way there is always a parent_id and name
        :param schematext:
        :return:
        """
        assert schematext
        schematext = j.core.tools.text_strip(schematext, replace=False)
        if schematext.find("name") == -1:
            if "\n" != schematext[-1]:
                schematext += "\n"
            schematext += 'name* = ""\n'
        if isinstance(self._parent, j.application.JSConfigClass):
            if schematext.find("parent_id") == -1:
                if "\n" != schematext[-1]:
                    schematext += "\n"
                schematext += "parent_id* = 0 (I)\n"
        return schematext

    @property
    def _model(self):
        if self._model_ is None:
            # self._log_debug("Get model for %s"%self.__class__._location)
            bcdb = self._bcdb_selector()
            if "_SCHEMATEXT" in self.__class__.__dict__:
                s = self.__class__._SCHEMATEXT
            else:
                s = self.__class__._CHILDCLASS._SCHEMATEXT
            t = self._process_schematext(s)
            self._model_ = bcdb.model_get_from_schema(t)
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
        if self.exists(name=name):
            raise RuntimeError("obj: %s already exists" % name)
        return self._new(name=name, jsxobject=jsxobject, **kwargs)

    def _new(self, name, jsxobject=None, **kwargs):
        """
        :param name: for the CONFIG item (is a unique name for the service, client, ...)
        :param jsxobject: you can right away specify the jsxobject
        :param kwargs: the data elements which will be given to JSXObject underneith (given to constructor)
        :return: the service
        """
        if not jsxobject:
            jsxobject = self._model.new(data=kwargs)
            jsxobject.name = name

        # means we need to remember the parent id
        if isinstance(self._parent, j.application.JSConfigClass):
            if not self._parent._id:
                self._parent.save()
                assert self._parent._id
            jsxobject.parent_id = self._parent._id
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
            jsconfig = self._new(name=name, **kwargs)
        else:
            # check that the stored values correspond with kwargs given
            changed = False
            for key, val in kwargs.items():
                if not getattr(jsconfig, key) == val:
                    changed = True
                    setattr(jsconfig, key, val)
                    # msg = "COULD NOT GET OBJ BECAUSE KWARGS GIVEN DO NOT CORRESPOND WITH OBJ IN DB\n"
                    # msg += "kwargs: key:%s val:%s\n" % (key, val)
                    # msg += "object was:\n%s\n" % jsconfig._data._ddict_hr_get()
                    # raise RuntimeError(msg)
            if changed:
                jsconfig.save()

        jsconfig._triggers_call(jsconfig, "get")
        # if kwargs:
        #     jsconfig._data_update(kwargs)
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

        self._log_debug("get child:'%s'from '%s'" % (name, self._name))

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
            if not name in self._children:
                r = self._new(name=name, jsxobject=jsxobject)
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

        if isinstance(self._parent, j.application.JSConfigClass):
            if not self._parent._id:
                self._parent.save()
                assert self._parent._id
            kwargs["parent_id"] = str(self._parent._id)

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
        if self.exists(name=name):
            o = self.get(name)
            o.delete()

    def exists(self, name):
        res = self._findData(name=name)
        if len(res) > 1:
            raise RuntimeError("found too many items for :%s, name:\n%s\n%s" % (self.__class__.__name__, name, res))
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
        for item in self.find():
            if item not in x:
                x.append(item)
        return self._filter(filter=filter, llist=x, nameonly=False)

    def __getattr__(self, name):
        # if private or non child then just return

        if isinstance(self, j.application.JSConfigClass):
            if name in self._model.schema.propertynames:
                return self._data.__getattribute__(name)

        if isinstance(self, j.application.JSConfigsClass):

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

        return self.__getattribute__(name)

    def __setattr__(self, key, value):

        if key.startswith("_"):
            self.__dict__[key] = value

        if isinstance(self, j.application.JSConfigClass):
            if key == "data":
                self.__dict__[key] = value

        assert "data" not in self.__dict__

        if "_data" in self.__dict__ and key in self._model.schema.propertynames:
            # if value != self._data.__getattribute__(key):
            self._log_debug("SET:%s:%s" % (key, value))
            # self._update_trigger(key, value)
            self._data.__setattr__(key, value)
        else:
            if key in ["_protected"]:
                self.__dict__[key] = value
            elif not self._protected or key in self._properties:
                self.__dict__[key] = value
            else:
                raise RuntimeError("protected property:%s" % key)
