from Jumpscale import j

"""
classes who use JSXObject for data storage but provide nice interface to enduser
"""


class JSConfig:
    def _init_pre(self, parent=None, jsxobject=None, datadict={}):

        self._parent = parent

        if self._parent:
            self._model = self._parent._model
        else:
            # is a fall back for situation we want to use a JSConfig class without factory JSConfigs
            self._model = j.application.bcdb_system.model_get_from_schema(self.__class__._SCHEMATEXT)

        # self._model._kosmosinstance = self

        if jsxobject:
            self._data = jsxobject
        else:
            self._data = self._model.schema.new()  # create an empty object

        if datadict:
            self._data_update(datadict)

        assert self._data.name  # need to make sure name exists

    # def _obj_cache_reset(self):
    #     """
    #     puts the object back to its basic state
    #     :return:
    #     """
    #     JSBase._obj_cache_reset(self)
    #     self.__dict__["_data"] = None

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
        self._triggers_call(self, "delete")
        assert self._model
        self._model.delete(self.data)
        if self._parent:
            if self.data.name in self._parent._children:
                del self._parent._children[self.data.name]
        self._triggers_call(self, "delete_post")

    def save(self):
        assert self._model
        self._triggers_call(self, "delete")
        self.data.save()
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

    def __dataprops_names_get(self, filter=None):
        """
        e.g. in a JSConfig object would be the names of properties of the jsxobject = data
        e.g. in a JSXObject would be the names of the properties of the data itself

        :return: list of the names
        """
        # return self.__filter(filter=filter, llist=self.__names_methods_)

    # def __dir__(self):
    #     items = [key for key in self.__dict__.keys() if not key.startswith("_")]
    #     for item in self._schema.propertynames:
    #         if item not in items:
    #             items.append(item)
    #     items.sort()
    #     return items

    def __getattr__(self, attr):
        if attr.startswith("_"):
            return self.__getattribute__(attr)
        if attr in self._schema.propertynames:
            return self._data.__getattribute__(attr)

        return self.__getattribute__(attr)

    def __setattr__(self, key, value):
        if key.startswith("_") or key == "data":
            self.__dict__[key] = value

        elif "data" in self.__dict__ and key in self._schema.propertynames:
            # if value != self._data.__getattribute__(key):
            self._log_debug("SET:%s:%s" % (key, value))
            self._update_trigger(key, value)
            self.__dict__["data"].__setattr__(key, value)
        else:
            self.__dict__[key] = value

    def __str__(self):
        out = "## "
        out += "{BLUE}%s{RESET} " % self.__class__._location
        out += "{GRAY}Instance: "
        out += "{RED}'%s'{RESET} " % self.name
        out += "{GRAY}\n"
        out += self._data._hr_get()  # .replace("{","[").replace("}","]")
        out += "{RESET}\n\n"
        out = j.core.tools.text_strip(out)
        # out = out.replace("[","{").replace("]","}")

        # TODO: *1 dirty hack, the ansi codes are not printed, need to check why
        print(out)
        return ""

    __repr__ = __str__
