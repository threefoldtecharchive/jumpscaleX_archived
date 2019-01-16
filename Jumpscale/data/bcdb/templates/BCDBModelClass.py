from Jumpscale import j
#GENERATED CODE CAN CHANGE

SCHEMA="""
{{schema_text}}
"""

bcdb = j.data.bcdb.latest
schema = j.data.schema.get(SCHEMA)

Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema,__file__)
MODEL_CLASS = bcdb._BCDBModelClass


class {{BASENAME}}(Index_CLASS,MODEL_CLASS):
    def __init__(self,bcdb,schema,reset=False):
        MODEL_CLASS.__init__(self, bcdb=bcdb,schema=schema,reset=reset)
        self.readonly = False
        self._init()

