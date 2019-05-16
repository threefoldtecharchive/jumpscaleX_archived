from Jumpscale import j


SCHEMA = """
@url = jumpscale.bcdb.group
name* = ""
dm_id* = ""
email* = ""  
user_members = (LI)
group_members = (LI)

"""


bcdb = j.data.bcdb.latest
schema = j.data.schema.get(SCHEMA)
MODEL_CLASS = bcdb._BCDBModelClass
Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema, __file__)


class GROUP(Index_CLASS, MODEL_CLASS):
    def __init__(self):
        MODEL_CLASS.__init__(self, bcdb=bcdb, schema=schema, custom=True)
        self._init()

    def userids_get(self):
        """
        will recursive get all users ids which are in group & return as list of id's of users
        :param id:
        :return:
        """
        if not id in self._groups:
            users = []
            gr = self.model_group.get(id)
            if gr:
                for userid in gr.users:
                    if userid not in users:
                        users.append(userid)
                for gid in gr.groups:
                    gr2 = self.model_group.get(id)
                    if gr2:
                        for userid2 in gr2.users:
                            if userid2 not in users:
                                users.append(userid2)
            self._groups[id] = users
        return self._groups[id]
