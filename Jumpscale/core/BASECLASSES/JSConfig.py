from Jumpscale import j
from .JSBase import JSBase

"""
classes who use JSXObject for data storage but provide nice interface to enduser
"""

from .Attr import Attr


class JSConfig(JSBase, Attr):
    def _init_pre(self, jsxobject=None, datadict={}, name=None):

        self._triggers = []

        if self._parent and "_model" in self._parent.__dict__:
            self._model = self._parent._model
        else:

            if "_SCHEMATEXT" in self.__class__.__dict__:
                s = self.__class__._SCHEMATEXT
            else:
                s = self._parent.__class__._SCHEMATEXT

            # is a fall back for situation we want to use a JSConfig class without factory JSConfigs
            self._model = j.application.bcdb_system.model_get_from_schema(s)

        # self._model._kosmosinstance = self

        if jsxobject:
            self._data = jsxobject
        else:
            jsxobjects = []
            if name:
                jsxobjects = self._model.find(name=name)
            if len(jsxobjects) > 0:
                self._data = jsxobjects[0]
            else:
                self._data = self._model.new()  # create an empty object

        if datadict:
            self._data_update(datadict)

        if name:
            self._data.name = name

    def _init_post(self, **kwargs):
        self._protected = True

    # def _obj_cache_reset(self):
    #     """
    #     puts the object back to its basic state
    #     :return:
    #     """
    #     JSBase._obj_cache_reset(self)
    #     self.__dict__["_data"] = None

    def __init_class_post(self):
        if isinstance(j.application.JSBaseConfigClass) and isinstance(j.application.JSBaseConfigsClass):
            raise RuntimeError("combination not allowed of config and configsclass")

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
        self._log_debug("trigger: %s:%s" % (jsconfig.name, action))
        for method in self._triggers:
            jsconfig = method(jsconfigs=self, jsconfig=jsconfig, action=action)
            assert isinstance(jsconfig, j.application.JSConfigClass)
        return jsconfig

    @property
    def _id(self):
        return self._data.id

    def _data_update(self, datadict):
        """
        will not automatically save the data, don't forget to call self.save()

        :param kwargs:
        :return:
        """
        # ddict = self._data._ddict  # why was this needed? (kristof)
        self._data._data_update(datadict=datadict)

    def delete(self):
        self._delete()

    def _delete(self):
        self._triggers_call(self, "delete")
        assert self._model
        self._model.delete(self._data)
        if self._parent:
            if self._data.name in self._parent._children:
                del self._parent._children[self._data.name]
        self._triggers_call(self, "delete_post")

    def save(self):
        self.save_()

    def save_(self):
        assert self._model
        self._triggers_call(self, "save")
        try:
            self._data.save()
        except:
            pass

        self._triggers_call(self, "save_post")

    def edit(self):
        """

        edit data of object in editor
        chosen editor in env var: "EDITOR" will be used

        :return:

        """
        path = j.core.tools.text_replace("{DIR_TEMP}/js_baseconfig_%s.toml" % self.__class__._location)
        data_in = self._data._toml
        j.sal.fs.writeFile(path, data_in)
        j.core.tools.file_edit(path)
        data_out = j.sal.fs.readFile(path)
        if data_in != data_out:
            self._log_debug(
                "'%s' instance '%s' has been edited (changed)" % (self._parent.__jslocation__, self._data.name)
            )
            data2 = j.data.serializers.toml.loads(data_out)
            self._data.data_update(data2)
        j.sal.fs.remove(path)

    def _dataprops_names_get(self, filter=None):
        """
        e.g. in a JSConfig object would be the names of properties of the jsxobject = data
        e.g. in a JSXObject would be the names of the properties of the data itself

        :return: list of the names
        """
        return self._filter(filter=filter, llist=self._model.schema.propertynames)
