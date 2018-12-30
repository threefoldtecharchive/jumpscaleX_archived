from Jumpscale import j
from .peeweeClient import PeeweeClient

import importlib

JSConfigFactory = j.application.JSFactoryBaseClass


class PeeweeFactory(j.application.JSBaseClass):
    """
    """
    __jslocation__ = "j.clients.peewee"
    _CHILDCLASS = PeeweeClient

    def _init(self):
        self.__imports__ = "peewee"
        self.clients = {}

        from .peewee import PrimaryKeyField, BlobField, Model, BooleanField, TextField, CharField, IntegerField,\
            SqliteDatabase, FloatField

        self.PrimaryKeyField = PrimaryKeyField
        self.BlobField = BlobField
        self.Model = Model
        self.BooleanField = BooleanField
        self.TextField = TextField
        self.CharField = CharField
        self.IntegerField = IntegerField
        self.SqliteDatabase = SqliteDatabase
        self.FloatField = FloatField

    # def getClient(self, ipaddr="localhost", port=5432, login="postgres", passwd="rooter", dbname="template"):
    #     key = "%s_%s_%s_%s_%s" % (ipaddr, port, login, passwd, dbname)
    #     if key not in self.clients:
    #         self.clients[key] = PostgresClient(
    #             ipaddr, port, login, passwd, dbname)
    #     return self.clients[key]

    # def getModelDoesntWorkYet(self, ipaddr="localhost", port=5432, login="postgres", passwd="rooter", dbname="template", dbtype="postgres", schema=None, cache=True):
    #     key = "%s_%s_%s_%s_%s" % (ipaddr, port, login, dbname, dbtype)
    #     if key not in self._cacheModel:
    #         pw = Pwiz(host=ipaddr, port=port, user=login, passwd=passwd, dbtype=dbtype, schema=schema, dbname=dbname)
    #         self._cacheModel[key] = pw.codeModel
    #     code = self._cacheModel[key]
    #     from IPython import embed
    #     embed()
    #     raise RuntimeError("stop debug here")

    def resetCache(self):
        for item in j.core.db.keys("peewee.*"):
            j.core.db.delete(item)
==== BASE ====

class PeeweeClient(JSConfigClient):
    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        c = self.config.data
        self.ipaddr = c['ipaddr']
        self.port = c['port']
        self.login = c['login']
        self.passwd = c['passwd_']
        self.dbname = c['dbname']
        self.dbtype = c['dbtype']
        self.schema = c['schema']
        self.cache = c['cache']
        self._model = None

    @property
    def model(self):
        if self._model:
            return self._model
        key = "%s_%s_%s_%s_%s" % (self.ipaddr, self.port, self.login, self.dbname, self.dbtype)

        if j.core.db.get("peewee.code.%s" % key) is None:
            cmd = 'pwiz.py -H %s  -p %s -u "%s" -P -i %s' % (self.ipaddr, self.port, self.login, self.dbname)
            rc, out, err = j.sal.process.execute(cmd, useShell=True, die=True, showout=False)
            j.core.db.set("peewee.code.%s" % key, out)
        code = j.core.db.get("peewee.code.%s" % key).decode()

        path = j.sal.fs.joinPaths(j.dirs.TMPDIR, "peewee", key + ".py")
        j.sal.fs.createDir(j.sal.fs.joinPaths(j.dirs.TMPDIR, "peewee"))
        j.sal.fs.writeFile(path, code)

        loader = importlib.machinery.SourceFileLoader(key, path)
        module = loader.load_module(key)

        self._model = module
        return module
==== BASE ====
