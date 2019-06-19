from Jumpscale import j


class NAMESPACE(j.data.bcdb._BCDBModelClass):
    def _init_load(self, bcdb, schema, reset):
        schema = j.data.schema.get_from_url_latest("jumpscale.bcdb.namespace.1")
        schema = bcdb._schema_add(schema)
        return bcdb, schema, reset

    @property
    def acl(self):
        raise RuntimeError("cannot modify acl object in acl object")
