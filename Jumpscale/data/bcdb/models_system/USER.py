from Jumpscale import j


SCHEMA = """

"""


bcdb = j.data.bcdb.latest
schema = j.data.schema.get(SCHEMA)
# Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema,__file__)
MODEL_CLASS = bcdb._BCDBModelClass
Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema, __file__)


class USER(Index_CLASS, MODEL_CLASS):
    def __init__(self):
        MODEL_CLASS.__init__(self, bcdb=bcdb, schema=schema, custom=True)

        self._init()

    # def find(self, name=None, dm_id=None, email=None):
    #     if dm_id:
    #         key = dm_id.lower()
    #     elif email:
    #         key = email.lower()
    #     elif name:
    #         key = name.lower()
    #     else:
    #         key = ""
    #
    #     if key not in self._users:
    #
    #         if dm_id is None:
    #             if dm_id:
    #                 dm_id = dm_id.lower()
    #             elif email:
    #                 email = email.lower()
    #             elif name:
    #                 name = name.lower()
    #             j.shell()
    #
    #         self._users[id] = self.model_user.get(id)
    #         if self._users[id] == None:
    #             raise RuntimeError("Could not find user:%s (name:%s dm_id:%s email:%s)" % (
    #                 id, name, dm_id, email))
    #
    #     return self._users[key]
