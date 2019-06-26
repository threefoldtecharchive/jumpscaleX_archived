from Jumpscale import j
from .JSBase import JSBase
import types


class JSBaseDataObj(JSBase):
    def __init__(self, jsxobject=None, datadict={}, parent=None, topclass=True, **kwargs):
        """
        :param kwargs: will be updated in the self.data object

        the self.data object is a jsobject (result of using the jsx schemas)

        """

        self._schema_ = None
        self._isnew = False

        JSBase.__init__(self, parent=parent, topclass=topclass, **kwargs)

        if jsxobject:
            if not isinstance(jsxobject, j.data.schema._JSXObjectClass):
                raise RuntimeError("data should be a jsxobject")
            self._data = jsxobject
        else:
            self._data = self._schema.new()

        self.data_update(datadict)

        if kwargs == {} and data == None:
            self.load()

    def load(self):
        pass

    @property
    def _schema(self):
        if self._schema_ is None:
            self._schema_ = j.data.schema.get_from_text(self.__class__._SCHEMATEXT)
        return self._schema_

    def __init_class_post(self):

        if not hasattr(self.__class__, "_SCHEMATEXT"):
            raise RuntimeError("need _SCHEMATEXT as class property.\n")

        self.__class__.__objcat_name = "instance"

    def _init_post(self, **kwargs):
        self._key = "%s:%s:%s" % (self.__class__._location, self.__class__._name, self.data.name)

    @property
    def _id(self):
        return self.data.id

    def data_update(self, datadict={}):
        """
        will not automatically save the data, don't forget to call self.save()
        datadict is a dict

        :param kwargs:
        :return:
        """
        ddict = self.data._ddict  # needed to make sure something is loaded
        self.data._data_update(data=datadict)

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

    def _update_trigger(self, key, val):
        pass

    def __dataprops_names_get(self, filter=""):
        return self.__filter(filter=filter, llist=self._schema.propertynames)

    def __dataprops_get(self, filter=None):
        """
        normally coming from a database e.g. BCDB
        e.g. disks in a server, or clients in SSHClientFactory
        if nothing then is self.__dataprops which is then normally = []

        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        :return:
        """
        j.shell()

    def __dataprop_get(self, name=None, id=None):
        """
        finds a dataprop coming from e.g. a database
        :param name:
        :param id:
        :return:
        """
        for item in self.__dataprops_get():
            if name:
                assert isinstance(name, str)
                if self.__name_get(item) == name:
                    return item
            elif id:
                id = int(id)
                if item.id == id:
                    return item
            else:
                raise RuntimeError("need to specify name or id")
        return None

    def __getattr__(self, attr):
        if attr.startswith("_"):
            return self.__getattribute__(attr)
        if attr in self._schema.propertynames:
            return self.data.__getattribute__(attr)

        return self.__getattribute__(attr)

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

    # def __str__(self):
    #     out = "## "
    #     out += "{BLUE}%s{RESET} " % self.__class__._location
    #     out += "{GRAY}Instance: "
    #     out += "{RED}'%s'{RESET} " % self.name
    #     out += "{GRAY}\n"
    #     out += self.data._hr_get()  # .replace("{","[").replace("}","]")
    #     out += "{RESET}\n\n"
    #     out = j.core.tools.text_strip(out)
    #     # out = out.replace("[","{").replace("]","}")
    #
    #     # TODO: *1 dirty hack, the ansi codes are not printed, need to check why
    #     print(out)
    #     return ""

    __repr__ = __str__
