from Jumpscale import j
from .JSBase import JSBase
import types


class JSBaseDataObj(JSBase):
    def __init__(self, data=None, parent=None, topclass=True, **kwargs):
        """
        :param kwargs: will be updated in the self.data object

        the self.data object is a jsobject (result of using the jsx schemas)

        """

        JSBase.__init__(self, parent=parent, topclass=False)

        self._schema_ = None

        self._isnew = False

        if data:
            if not isinstance(data, j.data.schema._JSXObjectClass):
                raise RuntimeError("data should be a jsobj")
            self.data = data
        else:
            self.data = self._schema.new()

        self._data_update(**kwargs)

        if topclass:
            self._init2(**kwargs)
            self._init()

        if kwargs == {} and data == None:
            self.load()

    def load(self):
        pass

    @property
    def _schema(self):
        if self._schema_ is None:
            self._schema_ = j.data.schema.get_from_text(self.__class__._SCHEMATEXT)
        return self._schema_

    def _class_init(self):

        if not hasattr(self.__class__, "_class_init_done"):

            if not hasattr(self.__class__, "_SCHEMATEXT"):
                raise RuntimeError("need _SCHEMATEXT as class property.\n")

            # always needs to be in this order at end
            JSBase._class_init(self)
            self.__class__.__objcat_name = "instance"

            # print("classinit:%s"%self.__class__)

    def _init2(self, **kwargs):
        self._key = "%s:%s:%s" % (self.__class__._location, self.__class__._name, self.data.name)
        # self.data._autosave = True
        # always needs to be last
        JSBase._init2(self, **kwargs)

    # def _obj_cache_reset(self):
    #     """
    #     puts the object back to its basic state
    #     :return:
    #     """
    #     JSBase._obj_cache_reset(self)
    #     self.__dict__["_data"] = None

    @property
    def _id(self):
        return self.data.id

    def _data_update(self, **kwargs):
        """
        will not automatically save the data, don't forget to call self.save()

        :param kwargs:
        :return:
        """
        ddict = self.data._ddict
        self.data._data_update(data=kwargs)

    def edit(self):
        """

        edit data of object in editor
        chosen editor in env var: "EDITOR" will be used

        :return:

        """
        path = j.core.tools.text_replace("{DIR_TEMP}/js_baseconfig_%s.toml" % self.__class__._location)
        data_in = self.data._toml
        j.sal.fs.writeFile(path, data_in)
        j.core.tools.file_edit(path)
        data_out = j.sal.fs.readFile(path)
        if data_in != data_out:
            self._log_debug(
                "'%s' instance '%s' has been edited (changed)" % (self._parent.__jslocation__, self.data.name)
            )
            data2 = j.data.serializers.toml.loads(data_out)
            self.data.data_update(data2)
        j.sal.fs.remove(path)

    # def view(self):
    #     path = j.core.tools.text_replace("{DIR_TEMP}/js_baseconfig_%s.toml" % self.__class__._location)
    #     data_in = self.data._toml
    #     j.tools.formatters.print_toml(data_in)

    def __dir__(self):
        items = [key for key in self.__dict__.keys() if not key.startswith("_")]
        for item in self._schema.propertynames:
            if item not in items:
                items.append(item)
        items.sort()
        return items

    def __getattr__(self, attr):
        if attr.startswith("_"):
            return self.__getattribute__(attr)
        if attr in self._schema.propertynames:
            return self.data.__getattribute__(attr)

        return self.__getattribute__(attr)

    def _update_trigger(self, key, val):
        pass

    def __setattr__(self, key, value):
        if key.startswith("_") or key == "data":
            self.__dict__[key] = value

        elif "data" in self.__dict__ and key in self._schema.propertynames:
            # if value != self.data.__getattribute__(key):
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
        out += self.data._hr_get()  # .replace("{","[").replace("}","]")
        out += "{RESET}\n\n"
        out = j.core.tools.text_strip(out)
        # out = out.replace("[","{").replace("]","}")

        # TODO: *1 dirty hack, the ansi codes are not printed, need to check why
        print(out)
        return ""

    __repr__ = __str__
