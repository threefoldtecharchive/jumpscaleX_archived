from Jumpscale import j


JSBASE = j.application.JSBaseClass


class DBSQLite(j.application.JSBaseClass):
    def __init__(self, bcdb):
        JSBASE.__init__(self)
        self.bcdb = bcdb

        self._dbpath = j.sal.fs.joinPaths(bcdb._data_dir, "sqlite.db")

        if j.sal.fs.exists(self._dbpath):
            self._log_debug("EXISTING SQLITEDB in %s" % self._dbpath)
        else:
            self._log_debug("NEW SQLITEDB in %s" % self._dbpath)

        self.sqlitedb = j.clients.peewee.SqliteDatabase(self._dbpath)
        if self.sqlitedb.is_closed():
            self.sqlitedb.connect()

        p = j.clients.peewee

        class BaseModel(p.Model):
            class Meta:
                database = self.sqlitedb

        class KVS(BaseModel):
            id = p.PrimaryKeyField()
            value = p.BlobField()

        self._table_model = KVS
        #
        self._table_model.create_table()

    def set(self, key, val):
        if key == None:
            res = self._table_model(value=val)
            res.save()
            return res.id
        else:
            key = int(key)
            if self.exists(key):
                self._table_model.update(value=val).where(self._table_model.id == key).execute()
            else:
                self._table_model.create(id=key, value=val)
        v = self.get(key)
        return key

    def exists(self, key):
        return self.count(key) > 0

    def count(self, key):
        return self._table_model.select().where(self._table_model.id == key).count()

    def get(self, key):
        res = self._table_model.select().where(self._table_model.id == key)
        if len(res) == 0:
            return None
        elif len(res) > 1:
            raise RuntimeError("error, can only be 1 item")
        return res[0].value

    def delete(self, key):
        self._table_model.delete_by_id(key)

    # def reset(self):
    #     self._log_info("RESET FOR KVS")
    #     self._table_model.delete().execute()
    #     self._table_model.create_table()
    #     assert self._table_model.select().count() == 0

    def iterate(self, key_start=None, **kwargs):
        if key_start:
            items = self._table_model.select().where(getattr(self._table_model, id) >= key_start)
        else:
            items = self._table_model.select()
        for item in items:
            yield (item.id, self.get(item.id))

    def close(self):
        self.sqlitedb.close()
