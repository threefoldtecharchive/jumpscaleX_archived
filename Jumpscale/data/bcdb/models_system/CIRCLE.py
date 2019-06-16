from Jumpscale import j


class CIRCLE(j.data.bcdb._BCDBModelClass):
    def _init_load(self, bcdb, schema, namespaceid, reset):
        schema = j.data.schema.get_from_url_latest("jumpscale.bcdb.circle.1")
        schema = bcdb._schema_add(schema)
        return bcdb, schema, namespaceid, reset

    def userids_get(self):
        """
        will recursive get all users ids which are in circle & return as list of id's of users
        :param id:
        :return:
        """
        if not id in self._circles:
            users = []
            gr = self.model_circle.get(id)
            if gr:
                for userid in gr.users:
                    if userid not in users:
                        users.append(userid)
                for gid in gr.circles:
                    gr2 = self.model_circle.get(id)
                    if gr2:
                        for userid2 in gr2.users:
                            if userid2 not in users:
                                users.append(userid2)
            self._circles[id] = users
        return self._circles[id]
