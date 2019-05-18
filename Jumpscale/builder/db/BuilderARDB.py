from Jumpscale import j


class BuilderARDB(j.builder.system._BaseClass):
    NAME = "ardb"

    def reset(self):
        app.reset(self)
        self._init()

    def _init(self):
        self.BUILDDIRFDB = self._replace("{DIR_VAR}/build/forestdb/")
        self.CODEDIRFDB = self._replace("{DIR_CODE}/github/couchbase/forestdb")
        self.CODEDIRARDB = self._replace("{DIR_CODE}/github/yinqiwen/ardb")
        self.BUILDDIRARDB = self._replace("{DIR_VAR}/build/ardb/")

    def buildForestDB(self, reset=False):

        if self._done_check("buildforestdb", reset):
            return

        j.builder.system.package.ensure(["git-core", "cmake", "libsnappy-dev", "g++"])

        url = "git@github.com:couchbase/forestdb.git"
        cpath = j.clients.git.pullGitRepo(url, tag="v1.2", reset=reset)

        assert cpath.rstrip("/") == self.CODEDIRFDB.rstrip("/")

        C = """
            set -ex
            cd {DIR_CODE}FDB
            mkdir build
            cd build
            cmake ../
            make all
            rm -rf {DIR_VAR}/build/FDB/
            mkdir -p {DIR_VAR}/build/FDB
            cp forestdb_dump* {DIR_VAR}/build/FDB/
            cp forestdb_hexamine* {DIR_VAR}/build/FDB/
            cp libforestdb* {DIR_VAR}/build/FDB/
            """
        j.sal.process.execute(self._replace(C))
        self._done_set("buildforestdb")

    def build(self, destpath="", reset=False):
        """
        @param destpath, if '' then will be {DIR_TEMP}/build/openssl
        j.builder.db.ardb.build()
        """
        j.shell()
        if self._done_check("build", reset):
            return

        if self.tools.command_check("ardb-server") and not reset:
            return

        if reset:
            j.sal.process.execute("rm -rf %s" % self.BUILDDIR)

        # not needed to build separately is done in ardb automatically
        # self.buildForestDB(reset=reset)

        self.buildARDB(reset=reset)
        self._done_set("build")

    # TODO: which one is it ??? 2 builders
    def build2(self, reset=False, storageEngine="forestdb"):
        """
        kosmos 'j.builder.db.ardb.build()'

        @param storageEngine rocksdb or forestdb
        """
        if self._done_check("buildardb", reset):
            return

        # Default packages needed
        packages = ["wget", "bzip2"]

        if j.builder.platformtype.isMac:
            storageEngine = "rocksdb"
            # ForestDB
            packages += ["git", "cmake", "libsnappy-dev", "gcc48"]
            # j.builder.system.package.ensure("boost")
        else:
            # ForestDB
            packages += ["git", "cmake", "libsnappy-dev", "g++"]
            # RocksDB
            packages += ["libbz2-dev"]

        # PerconaFT
        packages += ["unzip"]

        # Install dependancies
        j.builder.system.package.ensure(packages)

        url = "https://github.com/yinqiwen/ardb.git"
        cpath = j.clients.git.pullGitRepo(url, tag="v0.9.3", reset=reset, ssh=False)
        self._log_info(cpath)

        assert cpath.rstrip("/") == self.CODEDIRARDB.rstrip("/")

        C = """
            set -ex
            cd {DIR_CODE}ARDB
            # cp {DIR_VAR}/build/FDB/libforestdb* .
            storage_engine=$storageEngine make
            rm -rf {DIR_VAR}/build/ARDB/
            mkdir -p {DIR_VAR}/build/ARDB
            cp src/ardb-server {DIR_VAR}/build/ARDB/
            cp ardb.conf {DIR_VAR}/build/ARDB/
            """
        C = C.replace("$storageEngine", storageEngine)
        j.sal.process.execute(self._replace(C))

        self._done_set("buildardb")

    def install(self, name="main", host="localhost", port=16379, datadir=None, reset=False, start=True):
        """
        as backend use ForestDB
        """
        if self._done_check("install-%s" % name, reset):
            return
        self.buildARDB()
        j.core.tools.dir_ensure("{DIR_BIN}")
        j.core.tools.dir_ensure("$CFGDIR")
        if not j.builder.tools.file_exists("{DIR_BIN}/ardb-server"):
            j.builder.tools.file_copy("{DIR_VAR}/build/ardb/ardb-server", "{DIR_BIN}/ardb-server")

        # self.tools.profile.path_add('{DIR_BIN}')

        if datadir is None or datadir == "":
            datadir = self._replace("{DIR_VAR}/data/ardb/{}".format(name))
        j.core.tools.dir_ensure(datadir)

        # config = config.replace("redis-compatible-mode     no", "redis-compatible-mode     yes")
        # config = config.replace("redis-compatible-version  2.8.0", "redis-compatible-version  3.5.2")
        config = j.core.tools.file_text_read("{DIR_VAR}/build/ardb/ardb.conf")
        config = config.replace("${ARDB_HOME}", datadir)
        config = config.replace("0.0.0.0:16379", "{host}:{port}".format(host=host, port=port))

        cfg_path = "$CFGDIR/ardb/{}/ardb.conf".format(name)
        j.builder.tools.file_write(cfg_path, config)

        self._done_set("install-%s" % name)

        if start:
            self.start(name=name, reset=reset)

    def start(self, name="main", reset=False):
        if not reset and self._done_get("start-%s" % name):
            return

        cfg_path = "$CFGDIR/ardb/{}/ardb.conf".format(name)
        cmd = "{DIR_BIN}/ardb-server {}".format(cfg_path)
        pm = j.builder.system.processmanager.get()
        pm.ensure(name="ardb-server-{}".format(name), cmd=cmd, env={}, path="")
        # self.test(port=port)

        self._done_set("start-%s" % name)

    def stop(self, name="main"):
        pm = j.builder.system.processmanager.get()
        pm.stop("ardb-server-{}".format(name))

    def getClient(self):
        pass

    def test(self, port):
        """
        do some test through normal redis client
        """
        if j.builder.executor.type == "local":
            addr = "localhost"
        else:
            addr = j.builder.executor.addr

        r = j.clients.redis.get(ipaddr=addr, port=port)
        r.set("test", "test")
        assert r.get("test") == b"test"
        r.delete("test")
