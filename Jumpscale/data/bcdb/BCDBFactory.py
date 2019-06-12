from Jumpscale import j

from .BCDB import BCDB
from .BCDBModel import BCDBModel
import os
import sys
import redis


class BCDBFactory(j.application.JSBaseClass):

    __jslocation__ = "j.data.bcdb"

    def _init(self):

        self._log_debug("bcdb starts")
        self.bcdb_instances = {}  # key is the name
        self._path = j.sal.fs.getDirName(os.path.abspath(__file__))

        self._code_generation_dir = None
        self.latest = None

        j.clients.redis.core_get()  # just to make sure the redis got started

        j.data.schema.add_from_path("%s/models_system/meta.toml" % self._dirpath)

        self._config_data_path = j.core.tools.text_replace("{DIR_CFG}/bcdb_config")
        if j.sal.fs.exists(self._config_data_path):
            data_encrypted = j.sal.fs.readFile(self._config_data_path, binary=True)
            data = j.data.nacl.default.decryptSymmetric(data_encrypted)
            self._config = j.data.serializers.msgpack.loads(data)
        else:
            self._config = {}

    @property
    def _BCDBModelClass(self):
        return BCDBModel

    def index_rebuild(self):
        """
        kosmos 'j.data.bcdb.index_rebuild()'
        :return:
        """
        for name, data in self._config.items():
            if data["type"] == "zdb":
                zdbclient = j.clients.zdb.client_get(**data)
                bcdb = self.get(name, zdbclient)
                bcdb.index_rebuild()
            else:
                bcdb = self.get(name)
                bcdb.index_rebuild()

    def reset(self):
        """
        will remove all remembered connections
        :return:
        """
        j.sal.fs.remove(self._config_data_path)
        self._config = {}
        self.bcdb_instances = {}

    def destroy_all(self):
        """
        destroy all remembered BCDB's
        SUPER DANGEROUS
        all data will be lost
        :return:
        """
        # TODO: implement
        raise RuntimeError("not implemented")

    def get(self, name, zdbclient=None, reset=False, if_not_exist_die=False):
        """
        will create a new one or an existing one if it exists
        :param name:
        :param zdbclient:
        :param reset: means do not use an existing one
        :param if_not_exist_die, if True then will die if the instance does not exist yet
        :return:
        """
        if reset:
            if name in self.bcdb_instances:
                self.bcdb_instances.pop(name)
            if name in self._config:
                self._config.pop(name)

        data = {}
        if name in self.bcdb_instances:
            return self.bcdb_instances[name]
        elif name in self._config:
            data = self._config[name]
            if data["type"] == "zdb":
                if "admin" in data:
                    if data["admin"]:
                        raise RuntimeError("can only use ZDB connection which is not admin")
                    data.pop("admin")
                zdbclient = j.clients.zdb.client_get(**data)
            else:
                zdbclient = None
        elif if_not_exist_die:
            raise RuntimeError("did not find bcdb with name:%s" % name)

        self._log_debug("new bcdb:%s" % name)
        if zdbclient != None and j.data.types.string.check(zdbclient):
            raise RuntimeError("zdbclient cannot be str")

        if not name in self._config:
            if zdbclient:
                data["nsname"] = zdbclient.nsname
                data["admin"] = zdbclient.admin
                data["addr"] = zdbclient.addr
                data["port"] = zdbclient.port
                data["mode"] = zdbclient.mode
                data["secret"] = zdbclient.secret
                data["type"] = "zdb"
            else:
                data["nsname"] = name
                data["type"] = "sqlite"

            self._config[name] = data
            data = j.data.serializers.msgpack.dumps(self._config)
            data_encrypted = j.data.nacl.default.encryptSymmetric(data)
            j.sal.fs.writeFile(self._config_data_path, data_encrypted)

        self.bcdb_instances[name] = BCDB(zdbclient=zdbclient, name=name, reset=reset)
        return self.bcdb_instances[name]

    def new(self, name, zdbclient=None):
        """
        create a new instance (can also do this using self.new(...))
        :param name:
        :param zdbclient: optional
        :return:
        """
        return self.get(name=name, zdbclient=zdbclient)

    def bcdb_test_get(self, reset=True):
        bcdb = j.data.bcdb.get(name="test", zdbclient=None, reset=reset)
        assert j.data.bcdb.latest.zdbclient == None
        return bcdb

    def redis_server_start(
        self,
        name="test",
        reset=False,
        ipaddr="localhost",
        port=6380,
        background=False,
        secret="123456",
        zdbclient_addr="localhost",
        zdbclient_port=9900,
        zdbclient_namespace="test",
        zdbclient_secret="1234",
        zdbclient_mode="seq",
    ):

        """
        start a redis server on port 6380 on localhost only

        you need to feed it with schema's

        if zdbclient_addr is None, will use sqlite embedded backend

        trick: use RDM to investigate (Redis Desktop Manager) to investigate DB.

        kosmos "j.data.bcdb.redis_server_start(background=True)"

        kosmos "j.data.bcdb.redis_server_start(background=False,zdbclient_addr=None)"


        :return:
        """

        if background:

            args = 'ipaddr="%s", ' % ipaddr
            args += 'name="%s", ' % name
            args += "port=%s, " % port
            args += 'secret="%s", ' % secret
            args += 'zdbclient_addr="%s", ' % zdbclient_addr
            args += "zdbclient_port=%s, " % zdbclient_port
            args += 'zdbclient_namespace="%s", ' % zdbclient_namespace
            args += 'zdbclient_secret="%s", ' % zdbclient_secret
            args += 'zdbclient_mode="%s"' % zdbclient_mode

            cmd = "kosmos 'j.data.bcdb.redis_server_start(%s)'" % args

            cmdcmd = j.tools.startupcmd.get(name="bcdbredis_%s" % port, cmd=cmd, ports=[port])

            cmdcmd.start(reset=reset)

            j.sal.nettools.waitConnectionTest(ipaddr=ipaddr, port=port, timeoutTotal=5)
            r = j.clients.redis.get(ipaddr=ipaddr, port=port, password=secret)
            assert r.ping()

        else:
            if zdbclient_addr not in ["None", None]:
                zdbclient = j.clients.zdb.client_get(
                    nsname=zdbclient_namespace,
                    addr=zdbclient_addr,
                    port=zdbclient_port,
                    secret=zdbclient_secret,
                    mode=zdbclient_mode,
                )
            else:
                zdbclient = None
            bcdb = self.new(name, zdbclient=zdbclient)
            bcdb.redis_server_start(port=port)

    @property
    def code_generation_dir(self):
        if not self._code_generation_dir:
            path = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "models")
            j.sal.fs.createDir(path)
            if path not in sys.path:
                sys.path.append(path)
            j.sal.fs.touch(j.sal.fs.joinPaths(path, "__init__.py"))
            self._log_debug("codegendir:%s" % path)
            self._code_generation_dir = path
        return self._code_generation_dir

    def _load_test_model(self, reset=True, sqlitestor=False):

        schema = """
        @url = despiegk.test
        llist2 = "" (LS)
        name** = ""
        email** = ""
        nr** = 0
        date_start** = 0 (D)
        description = ""
        token_price** = "10 USD" (N)
        hw_cost = 0.0 #this is a comment
        llist = []
        llist3 = "1,2,3" (LF)
        llist4 = "1,2,3" (L)
        llist5 = "1,2,3" (LI)
        U = 0.0
        pool_type = "managed,unmanaged" (E)
        """
        if self.latest != None:
            self.latest.stop()
        if sqlitestor:
            bcdb = j.data.bcdb.get(name="test", zdbclient=None, reset=reset)
            assert j.data.bcdb.latest.zdbclient == None
            if reset:
                bcdb.reset()  # empty
        else:
            zdbclient_admin = j.servers.zdb.start_test_instance(destroydata=reset)
            zdbclient = zdbclient_admin.namespace_new("test", secret="1234")
            bcdb = j.data.bcdb.get(name="test", zdbclient=zdbclient, reset=reset)

        schemaobj = j.data.schema.get_from_text(schema)
        bcdb.model_get_from_schema(schemaobj)

        self._log_debug("bcdb already exists")

        model = bcdb.model_get_from_url("despiegk.test")

        return bcdb, model

    def test(self, name=""):
        """
        following will run all tests

        kosmos 'j.data.bcdb.test()'


        """

        cla = j.servers.zdb.start_test_instance(destroydata=True, namespaces=["test"])
        cl = cla.namespace_get("test", "1234")
        assert cla.ping()
        assert cl.ping()

        bcdb = j.data.bcdb.new("test", zdbclient=cl)

        bcdb.reset()

        self._test_run(name=name)

        j.servers.zdb.stop()
        redis = j.tools.tmux.cmd_get("bcdbredis_6380")
        redis.stop()
        self._log_info("All TESTS DONE")
        return "OK"
