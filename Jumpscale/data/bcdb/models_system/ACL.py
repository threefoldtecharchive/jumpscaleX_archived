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

# print("***IMPORT ACL****")
bcdb = j.data.bcdb.latest
schema = j.data.schema.get(SCHEMA)

Index_CLASS = bcdb._BCDBModelIndexClass_generate(schema, __file__)
MODEL_CLASS = bcdb._BCDBModelClass


class ACL(Index_CLASS, MODEL_CLASS):
    def __init__(self):
        MODEL_CLASS.__init__(self, bcdb=bcdb, schema=schema, custom=True)
        Index_CLASS.__init__(self)
        self.readonly = True
        self._init()

    @property
    def acl(self):
        raise RuntimeError("cannot modify acl object in acl object")

    def rights_set(self, acl, userids=[], groupids=[], rights="r"):
        """
        userid can be list of userid or userid
        :param acl:
        :param users:
        :param rights:
        :return:
        """

        rights = j.data.types.string.unique_sort(rights).lower()  # lets make sure its sorted & unique

        if not j.data.types.list.check(userids):
            raise RuntimeError("userids needs to be list")
        if not j.data.types.list.check(groupids):
            raise RuntimeError("groupids needs to be list")

        rdict = acl._ddict

        change = False

        def do(itemsToFind, rdict, key, rights, change):
            found = []
            group = rdict[key]

            for i in itemsToFind:
                i = int(i)
                if i in group:
                    original = j.data.types.string.unique_sort(group[i]).lower()
                    if original != rights:
                        change = True
                        group[i] = rights
                else:
                    # does not exist yet
                    change = True
                    group[i] = rights
            return change, rdict

        change, rdict = do(userids, rdict, "users", rights, change)
        change, rdict = do(groupids, rdict, "groups", rights, change)

        if change:
            if self.readonly:
                if acl.id is not None:
                    # means there is a change
                    acl.readonly = False  # acl will become a new one, the id is removed
                    acl.load_from_data(data=rdict, keepid=False, keepacl=False)
                    assert acl.id is None
                else:
                    acl.readonly = False
                    acl.load_from_data(data=rdict, keepid=True, keepacl=False)
            else:
                acl.readonly = False
                acl.load_from_data(data=rdict, keepid=True, keepacl=False)

            dosave, acl = self._set_pre(acl)
            if dosave:
                acl.save()

        return change

    def rights_check(self, acl, userid, rights):
        def rights_check2(rights2check, rightsInObj):
            for item in rights2check:
                if item not in rightsInObj:
                    return False
            return True

        userid = int(userid)
        for user in acl.users:
            if user.uid == userid:
                return rights_check2(rights, user.rights)
        for group in acl.groups:
            group = acl.model.bcdb.group.get(group)
            if group:
                if group.user_exists(userid):
                    if rights_check2(rights, group.rights):
                        return True
        return False

    def _methods_add(self, obj):
        obj.rights_set = types.MethodType(self.rights_set, obj)
        obj.rights_check = types.MethodType(self.rights_check, obj)
        obj._readonly = True

        return obj

    def _dict_process_out(self, d):
        res = {}
        self._log_debug("dict_process_out:\n%s" % d)
        for group in d["groups"]:
            r = j.data.types.list.clean(group["rights"])
            r = "".join(r)
            res[group["uid"]] = r  # as string
        d["groups"] = res
        res = {}
        for user in d["users"]:
            r = j.data.types.list.clean(user["rights"])
            r = "".join(r)
            res[user["uid"]] = r  # as string
        d["users"] = res
        return d

    def _dict_process_in(self, d):
        res = {}
        res["hash"] = d["hash"]
        res["groups"] = []
        res["users"] = []
        for uid, rights in d["groups"].items():
            res["groups"].append({"uid": uid, "rights": rights})
        for uid, rights in d["users"].items():
            res["users"].append({"uid": uid, "rights": rights})
        self._log_debug("dict_process_in_result:\n%s" % res)
        return res

    def _set_pre(self, acl):
        """

        :param acl:
        :return:
        """
        acl.key = acl.hash

        hash = j.data.hash.md5_string(acl._json)
        if acl.hash == hash:
            if acl.id is not None:
                # means the object did not change nothing to do
                # and the object id is already known, so exists already in DB
                self._log_debug("acl alike, id exists")
                return False, acl
            else:
                self._log_debug("acl alike, new object")
                return True, acl  # is a new one need to save

        # now check if the acl hash is already in the index
        res = self.get_from_keys(hash=hash)
        if len(res) == 1:
            self._log_debug("acl is in index")
            return False, res[0]  # no need to save
        elif len(res) > 1:
            raise RuntimeError("more than 1 acl found based on hash")
        else:
            self._log_debug("new acl")
            # MEANS THE HASH IS DIFFERENT & not found in index
            if acl.id is not None:
                # acl already exists, no need to save but need to index
                # existing acl but hash differently, need to fetch new one & get data from existing one
                assert acl.hash != hash  # otherwise it should have been found in the get_from_keys above...
                acl2 = self.new(capnpbin=acl._data)
                acl = acl2
            acl.hash = hash
            return True, acl
