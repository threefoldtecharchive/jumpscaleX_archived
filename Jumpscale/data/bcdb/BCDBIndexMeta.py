from Jumpscale import j
import os

JSBASE = j.application.JSBaseClass


class IndexField():

    def __init__(self,property):
        self.name = property.name
        self.jumpscaletype = property.jumpscaletype
        if self.jumpscaletype.NAME == "string":
            self.type = "TextField"
        elif self.jumpscaletype.NAME in ["integer",'date']:
            self.type = "IntegerField"
        elif self.jumpscaletype.NAME in ["boolean"]:
            self.type = "BooleanField"
        elif self.jumpscaletype.NAME in ["numeric"]:
            self.type = "FloatField"
        elif self.jumpscaletype.NAME in ["float"]:
            self.type = "FloatField"
        else:
            j.shell()
            raise RuntimeError("did not find required type for peewee:%s"%self)

    def __str__(self):
        out = "indexfield:%s:%s:%s"%(self.name,self.type,self.jumpscaletype)
        return out

    __repr__ = __str__


class BCDBIndexMeta(JSBASE):
    def __init__(self,schema):
        """
        """
        JSBASE.__init__(self)
        self.schema=schema
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        self.fields = []
        self.fields_key = []

        for p in schema.index_properties:
            self.fields.append(IndexField(p))

        for p in schema.index_key_properties:
            self.fields_key.append(p.name)

        if len(self.fields)>0:
            self.active = True
        else:
            self.active = False

        if len(self.fields_key)>0:
            self.active_keys = True
        else:
            self.active_keys = False

    def __str__(self):
        out = "indexmodel:\s"
        for item in self.fields:
            out += " - "+str(item) + "\n"
        return out

    __repr__ = __str__

