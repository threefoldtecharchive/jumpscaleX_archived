from Jumpscale import j


class USER(j.data.bcdb._BCDBModelClass):
    def _init_load(self, bcdb, schema, namespaceid, reset):
        schema = j.data.schema.get_from_url_latest("jumpscale.bcdb.user.1")
        return bcdb, schema, namespaceid, reset

    @property
    def acl(self):
        raise RuntimeError("cannot modify acl object in acl object")
