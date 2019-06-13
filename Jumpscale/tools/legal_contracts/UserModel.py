from Jumpscale import j


SCHEMA = """
@url = jumpscale.bcdb.acl.1
groups = (LO) !jumpscale.bcdb.acl.group
users = (LO) !jumpscale.bcdb.acl.user
hash* = ""

@url = jumpscale.bcdb.acl.group
uid= 2147483647 (I)
rights = ""

@url = jumpscale.bcdb.acl.user
uid= 2147483647 (I)
rights = ""

"""

import types

bcdb = j.data.bcdb.bcdb_instances["legal"]
MODEL_CLASS = bcdb.model_class_get_from_schema(SCHEMA)


class UserModel(MODEL_CLASS):
    def __init__(self, bcdb):
        MODEL_CLASS.__init__(self, bcdb=bcdb)

    # def rights_check(self,acl,userid,rights):
    #     def rights_check2(rights2check,rightsInObj):
    #         for item in rights2check:
    #             if item not in rightsInObj:
    #                 return False
    #         return True
    #     userid=int(userid)
    #     for user in acl.users:
    #         if user.uid ==userid:
    #             return rights_check2(rights,user.rights)
    #     for group in acl.groups:
    #         group = acl.model.bcdb.group.get(group)
    #         if group:
    #             if group.user_exists(userid):
    #                 if rights_check2(rights,group.rights):
    #                     return True
    #     return False
    #
    def _methods_add(self, obj):
        obj.validate = types.MethodType(self.validate, obj)
        return obj

    def validate(self, obj):
        j.shell()
