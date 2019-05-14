from Jumpscale import j

import types


class ACL(j.data.bcdb._BCDBModelClass):

    def _init_load(self,bcdb,schema,namespaceid,reset):
        schema = j.data.schema.get_from_url_latest("jumpscale.bcdb.acl.1")
        return bcdb,schema,namespaceid,reset

    @property
    def acl(self):
        raise RuntimeError("cannot modify acl object in acl object")

    def rights_set(self,acl,userids=[],circleids=[],rights="r"):
        """
        userid can be list of userid or userid
        :param acl:
        :param users:
        :param rights:
        :return:
        """

        rights=j.data.types.string.unique_sort(rights).lower()  #lets make sure its sorted & unique

        if not j.data.types.list.check(userids):
            raise RuntimeError("userids needs to be list")
        if not j.data.types.list.check(circleids):
            raise RuntimeError("circleids needs to be list")

        rdict = acl._ddict

        change = False
        def do(itemsToFind,rdict,key, rights,change):
            found = []
            circle = rdict[key]

            for i in itemsToFind:
                i = int(i)
                if i in circle:
                    original=j.data.types.string.unique_sort(circle[i]).lower()
                    if original != rights:
                        change=True
                        circle[i]=rights
                else:
                    #does not exist yet
                    change=True
                    circle[i]=rights
            return change,rdict


        change,rdict = do(userids,rdict,"users",rights,change)
        change,rdict = do(circleids,rdict,"circles",rights,change)

        if change:
            acl._load_from_data(data=rdict)
            acl.save()

        return change

    def rights_check(self,acl,userid,rights):
        def rights_check2(rights2check,rightsInObj):
            for item in rights2check:
                if item not in rightsInObj:
                    return False
            return True
        userid=int(userid)
        for user in acl.users:
            if user.uid ==userid:
                return rights_check2(rights,user.rights)
        for circle in acl.circles:
            circle = acl.model.bcdb.circle.get(circle)
            if circle:
                if circle.user_exists(userid):
                    if rights_check2(rights,circle.rights):
                        return True
        return False

    def _methods_add(self,obj):
        """
        what does this do?
        :param self: 
        :param obj: 
        :return: 
        """
        obj.rights_set = types.MethodType(self.rights_set,obj)
        obj.rights_check = types.MethodType(self.rights_check,obj)
        obj._readonly = True

        return obj

    def _dict_process_out(self,d):
        res={}
        self._log_debug("dict_process_out:\n%s"%d)
        for circle in d["circles"]:
            r=j.data.types.list.clean(circle["rights"])
            r="".join(r)
            res[circle["uid"]]=r #as string
        d["circles"]=res
        res={}
        for user in d["users"]:
            r=j.data.types.list.clean(user["rights"])
            r="".join(r)
            res[user["uid"]]=r #as string
        d["users"]=res
        return d

    def _dict_process_in(self,d):
        res={}
        res["hash"]=d["hash"]
        res["circles"]=[]
        res["users"]=[]
        for uid,rights in d["circles"].items():
            res["circles"].append({"uid":uid,"rights":rights})
        for uid,rights in d["users"].items():
            res["users"].append({"uid":uid,"rights":rights})
        self._log_debug("dict_process_in_result:\n%s"%res)
        return res

