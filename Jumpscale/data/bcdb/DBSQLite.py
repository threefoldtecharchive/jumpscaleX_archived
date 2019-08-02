# Copyright (C) July 2018:  TF TECH NV in Belgium see https://www.threefold.tech/
# In case TF TECH NV ceases to exist (e.g. because of bankruptcy)
#   then Incubaid NV also in Belgium will get the Copyright & Authorship for all changes made since July 2018
#   and the license will automatically become Apache v2 for all code related to Jumpscale & DigitalMe
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.
# LICENSE END


from Jumpscale import j


JSBASE = j.application.JSBaseClass


class DBSQLite(j.application.JSBaseClass):
    def __init__(self, bcdb):
        JSBASE.__init__(self)
        if bcdb.storclient and bcdb.storclient.type == "RDB":
            raise j.exceptions.Base("cannot use sqlite for RDB")

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
            raise j.exceptions.Base("error, can only be 1 item")
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
