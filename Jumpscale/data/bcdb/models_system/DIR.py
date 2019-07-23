from Jumpscale import j


class DIR(j.data.bcdb._BCDBModelClass):
    def _schema_get(self):
        return j.data.schema.get_from_url_latest("jumpscale.bcdb.fs.dir.2")
