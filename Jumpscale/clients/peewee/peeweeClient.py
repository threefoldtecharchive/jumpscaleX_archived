import importlib
from Jumpscale import j
JSConfigClient = j.application.JSBaseConfigClass


class PeeweeClient(JSConfigClient):
    _SCHEMATEXT = """
    @url = jumpscale.peewee.client
    name* = "" (S)
    ipaddr = "localhost" (S)
    port = 0 (ipport)
    login = "postgres" (S)
    passwd_ = "" (S)
    dbname = "template" (S)
    dbtype = "postgres" (S)
    peeweeschema = "" (S)
    cache = true (B)
    """

    def _init(self):
        self.passwd = self.passwd_
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
