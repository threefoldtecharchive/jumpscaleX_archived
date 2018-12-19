
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class SchemaProperty(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)
        self.name = ""
        self.alias = ""
        self.default = ""
        self.jumpscaletype = None
        self.isList = False
        self.enumeration = []
        self.comment = ""
        self.pointer_type = None
        self.nr = 0
        self.index = False #as used in sqlite
        self.index_key = False #is for indexing the keys

        if self.name in ["schema"]:
            raise RuntimeError("cannot have property name:%s"%self.name)

    @property
    def default_as_python_code(self):
        if self.default == "''" or self.default == "\"\"":
            self.default = ""
        return self.jumpscaletype.python_code_get(self.default)

    @property
    def name_camel(self):
        out=""
        for item in self.name.split("_"):
            if out is "":
                out=item.lower()
            else:
                out+=item.capitalize()
        return out
            

    @property
    def js_typelocation(self):
        return "j.data.types.%s" % self.jumpscaletype.NAME

    @property
    def capnp_schema(self):
        return self.jumpscaletype.capnp_schema_get(self.name_camel, self.nr)

    def __str__(self):
        if not self.jumpscaletype.NAME == "list":
            out = "prop:%-25s (%s)"%(self.name,self.jumpscaletype.NAME)
        else:
            out = "prop:%-25s (%s(%s))"%(self.name,self.jumpscaletype.NAME,self.jumpscaletype.SUBTYPE.NAME)

        if self.default not in [None,0,"",[]]:
            out +="   default:%s"%self.default

        if self.pointer_type:
            out+=" !%s"%self.pointer_type
        return out
        
    __repr__ = __str__
