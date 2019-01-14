
import os
from copy import copy
from .SchemaProperty import SchemaProperty
from Jumpscale import j
import sys
sys.path.append("/sandbox/lib")


JSBASE = j.application.JSBaseClass


class Schema(j.application.JSBaseClass):
    def __init__(self, text):
        JSBASE.__init__(self)
        self.properties = []
        self._systemprops = {}
        self.lists = []
        self._obj_class = None
        self._capnp = None
        self._index_list = None
        self.url = ""
        self._schema_from_text(text)
        self.key = j.core.text.strip_to_ascii_dense(self.url).replace(".", "_")

        urls = self.url.split(".")
        if len(urls) > 0:
            try:
                # try if last one is version nr, if so pop it
                j.data.types.int.clean(urls[-1])
                self.version = urls.pop(len(urls) - 1)
                # will remove the version from the url
                self.url_noversion = ".".join(self.url.split(".")[:-1])
                if self.url_noversion in j.data.schema.schemas_versionless:
                    if j.data.schema.schemas_versionless[self.url_noversion].version < self.version+1:
                        # version itself can be replaced as well, there could be an update
                        j.data.schema.schemas_versionless[self.url_noversion] = self
                else:
                    j.data.schema.schemas_versionless[self.url_noversion] = self
            except:
                self.version = None
                self.url_noversion = None
            urls = ".".join(urls)

        j.data.schema.schemas[self.url] = self

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))

    def _error_raise(self, msg, e=None, schema=None):
        if self.url == "" and "url" in self._systemprops:
            self.url = self._systemprops["url"]
        out = "\nerror in schema:\n"
        out += "    url:%s\n" % self.url
        out += "    msg:%s\n" % j.core.text.prefix("    ", msg)
        if schema:
            out += "    schema:\n%s" % schema
        if e is not None:
            out += "\nERROR:\n"
            out += j.core.text.prefix("        ", str(e))
        raise RuntimeError(out)

    def _proptype_get(self, txt):
        """
        if default value specified in the schema, will check how to convert it to a type
        :param txt:
        :return:
        """
        if "\\n" in txt:
            jumpscaletype = j.data.types.multiline
            defvalue = jumpscaletype.fromString(txt)

        elif "'" in txt or '"' in txt:
            jumpscaletype = j.data.types.string
            defvalue = jumpscaletype.fromString(txt)

        elif "." in txt:
            jumpscaletype = j.data.types.float
            defvalue = jumpscaletype.fromString(txt)

        elif "true" in txt.lower() or "false" in txt.lower():
            jumpscaletype = j.data.types.bool
            defvalue = jumpscaletype.fromString(txt)

        elif "[]" in txt:
            jumpscaletype = j.data.types._list()
            jumpscaletype.SUBTYPE = j.data.types.string
            defvalue = []

        elif j.data.types.int.checkString(txt):  # means is digit
            jumpscaletype = j.data.types.int
            defvalue = jumpscaletype.fromString(txt)

        else:
            raise RuntimeError("cannot find type for:%s" % txt)

        return (jumpscaletype, defvalue)

    def _schema_from_text(self, text):
        """
        get schema object from schema text
        """

        self._logger.debug("load schema:\n%s" % text)

        self.text = j.core.text.strip(text)

        self._md5 = j.data.schema._md5(text)

        systemprops = {}
        self.properties = []
        # self._systemprops = systemprops

        def process(line):
            line_original = copy(line)
            propname, line = line.split("=", 1)
            propname = propname.strip()
            if ":" in propname:
                self._error_raise("Aliases no longer supported in names, remove  ':' in name '%s'" %
                                  propname, schema=text)
            line = line.strip()

            if "!" in line:
                line, pointer_type = line.split("!", 1)
                pointer_type = pointer_type.strip()
                line = line.strip()
            else:
                pointer_type = None

            if "#" in line:
                line, comment = line.split("#", 1)
                line = line.strip()
                comment = comment.strip()
            else:
                comment = ""

            p = SchemaProperty()

            name = propname+""  # make sure there is copy
            if name.endswith("**"):
                name = name[:-2]
                p.index = True
            if name.endswith("*"):
                name = name[:-1]
                p.index_key = True

            if name in ["id"]:
                self._error_raise("do not use 'id' in your schema, is reserved for system.", schema=text)

            if "(" in line:
                line_proptype = line.split("(")[1].split(")")[0].strip().lower()
                line_wo_proptype = line.split("(")[0].strip()
                if line_proptype == "o":
                    # special case where we have subject directly attached
                    jumpscaletype = j.data.types.get("jo")
                    jumpscaletype.SUBTYPE = pointer_type
                    defvalue = ""
                else:
                    if line_proptype in ["e", "enum"]:
                        try:
                            jumpscaletype = j.data.types.get_custom("e", values=line_wo_proptype)
                            defvalue = jumpscaletype.get_default()
                        except Exception as e:
                            self._error_raise("error (enum) on line:%s" % line_original, e=e)
                    else:
                        jumpscaletype = j.data.types.get(line_proptype)
                        try:
                            if line_wo_proptype == "" or line_wo_proptype is None:
                                defvalue = jumpscaletype.get_default()
                            else:
                                defvalue = jumpscaletype.fromString(line_wo_proptype)
                        except Exception as e:
                            self._error_raise("error on line:%s" % line_original, e=e)
            else:
                jumpscaletype, defvalue = self._proptype_get(line)

            p.name = name
            p.default = defvalue
            p.comment = comment
            p.jumpscaletype = jumpscaletype
            p.pointer_type = pointer_type

            return p

        nr = 0
        for line in text.split("\n"):
            line = line.strip()
            self._logger.debug("L:%s" % line)
            nr += 1
            if line.strip() == "":
                continue
            if line.startswith("@"):
                systemprop_name = line.split("=")[0].strip()[1:]
                systemprop_val = line.split("=")[1].strip()
                systemprops[systemprop_name] = systemprop_val.strip('"').strip("'")
                continue
            if line.startswith("#"):
                continue
            if "=" not in line:
                self._error_raise("did not find =, need to be there to define field", schema=text)

            p = process(line)

            if p.jumpscaletype.NAME is "list":
                self.lists.append(p)
            else:
                self.properties.append(p)

        for key, val in systemprops.items():
            self.__dict__[key] = val

        nr = 0
        for s in self.properties:
            s.nr = nr
            self.__dict__["property_%s" % s.name] = s
            nr += 1

        for s in self.lists:
            s.nr = nr
            self.__dict__["property_%s" % s.name] = s
            nr += 1

    @property
    def _capnp_id(self):
        if self._md5 == "":
            raise RuntimeError("hash cannot be empty")
        return "f" + self._md5[1:16]  # first bit needs to be 1

    @property
    def _capnp_schema(self):
        if not self._capnp:
            tpath = "%s/templates/schema.capnp" % self._path
            _capnp_schema_text = j.tools.jinja2.template_render(
                path=tpath, reload=False, obj=self, objForHash=self._md5)
            self._capnp = j.data.capnp.getSchemaFromText(_capnp_schema_text)
        return self._capnp

    @property
    def objclass(self):
        if self._obj_class is None:

            if self._md5 in [None, ""]:
                raise RuntimeError("md5 cannot be None")

            tpath = "%s/templates/template_obj.py" % self._path

            self._obj_class = j.tools.jinja2.code_python_render(
                name="schema_%s" % self.key, obj_key="ModelOBJ", path=tpath, obj=self, objForHash=self._md5)

        return self._obj_class

    def get(self, data=None, capnpbin=None, model=None):
        """
        get schema_object using data and capnpbin
        :param data:
        :param capnpbin:
        :param model: if a method given every change will call this method,
                        can be used to implement autosave
        :return:
        """
        if data is None:
            data = {}
        obj = self.objclass(schema=self, data=data, capnpbin=capnpbin, model=model)
        return obj

    def new(self, model=None, data=None):
        """
        get schema_object without any data
        """
        if data is None:
            data = {}
        r = self.get(data=data)
        if model is not None:
            model.notify_new(r)
        return r

    # @property
    # def propertynames_index_sql(self):
    #     """
    #     list of the property names which are used for indexing in sql db (sqlite)
    #     :return:
    #     """
    #     res=[]
    #     for prop in self.properties:
    #         if prop.index:
    #             res.append(prop.name)
    #     return res

    @property
    def properties_index_sql(self):
        """
        list of the properties which are used for indexing in sql db (sqlite)
        :return:
        """
        res = []
        for prop in self.properties:
            if prop.index:
                res.append(prop)
        return res

    # @property
    # def propertynames_index_keys(self):
    #     """
    #     list of the property names which are used for indexing with keys
    #     :return:
    #     """
    #     res=[]
    #     for prop in self.properties:
    #         if prop.index_key:
    #             res.append(prop.name)
    #     return res

    @property
    def properties_index_keys(self):
        """
        list of the properties which are used for indexing with keys
        :return:
        """
        res = []
        for prop in self.properties:
            if prop.index_key:
                res.append(prop)
        return res

    @property
    def propertynames(self):
        """
        lists all the property names
        :return:
        """
        res = [item.name for item in self.properties]
        for item in self.lists:
            res.append(item.name)
        return res

    # @property
    # def propertynames_list(self):
    #     res = [item.name for item in self.lists]
    #     return res

    @property
    def properties_list(self):
        res = [item for item in self.lists]
        return res

    # @property
    # def propertynames_nonlist(self):
    #     res = [item.name for item in self.properties]
    #     return res

    @property
    def properties_nonlist(self):
        res = [item for item in self.properties]
        return res

    def __str__(self):
        out = ""
        for item in self.properties:
            out += str(item) + "\n"
        for item in self.lists:
            out += str(item) + "\n"
        return out

    __repr__ = __str__
