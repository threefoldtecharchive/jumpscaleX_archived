from Jumpscale import j


JSBASE = j.application.JSBaseClass


class DBRedis(j.application.JSBaseClass):
    def __init__(self, bcdb):
        JSBASE.__init__(self)
        self.bcdb = bcdb

    def set(self, key, val):
        j.shell()
        return key

    def exists(self, key):
        j.shell()

    def count(self, key):
        j.shell()

    def get(self, key):
        j.shell()

    def delete(self, key):
        j.shell()

    def iterate(self, key_start=None, **kwargs):
        j.shell()
        if key_start:
            items = self._table_model.select().where(getattr(self._table_model, id) >= key_start)
        else:
            items = self._table_model.select()
        for item in items:
            yield (item.id, self.get(item.id))

    def close(self):
        pass
