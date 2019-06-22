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
        self._bcdb_instances = {}  # key is the name
        self._path = j.sal.fs.getDirName(os.path.abspath(__file__))

        self._code_generation_dir_ = None

        j.clients.redis.core_get()  # just to make sure the redis got started

        j.data.schema.add_from_path("%s/models_system/meta.toml" % self._dirpath)

        self._config_data_path = j.core.tools.text_replace("{DIR_CFG}/bcdb_config")
        if j.sal.fs.exists(self._config_data_path):
            data_encrypted = j.sal.fs.readFile(self._config_data_path, binary=True)
            try:
                data = j.data.nacl.default.decryptSymmetric(data_encrypted)
            except Exception as e:
                if str(e).find("Ciphertext failed") != -1:
                    raise RuntimeError("%s cannot be decrypted with secret" % self._config_data_path)
            self._config = j.data.serializers.msgpack.loads(data)
        else:
            self._config = {}

        self._system = None

    def get_system(self, reset=False):
        """
        sqlite based BCDB, don't need ZDB for this
        :return:
        """
        if not self._system:
            self._system = self.get("system", reset=reset)
        return self._system

    def get_test(self, reset=False):
        bcdb = j.data.bcdb.get(name="testbcdb", storclient=None, reset=reset)
        bcdb2 = j.data.bcdb._bcdb_instances["testbcdb"]
        assert bcdb2.storclient == None
        return bcdb

    @property
    def _BCDBModelClass(self):
        return BCDBModel

    @property
    def instances(self):
        res = []
        for name, data in self._config.items():
            if data["type"] == "zdb":
                storclient = j.clients.zdb.client_get(**data)
                bcdb = self.get(name, storclient)

            if data["type"] == "rdb":
                storclient = j.clients.rdb.client_get(**data)
                bcdb = self.get(name, storclient)
            else:
                bcdb = self.get(name)
            res.append(bcdb)
        return res

    def index_rebuild(self):
        """
        kosmos 'j.data.bcdb.index_rebuild()'
        :return:
        """
        for bcdb in self.instances:
            bcdb.index_rebuild()

    def reset(self):
        """
        will remove all remembered connections
        :return:
        """
        j.sal.fs.remove(self._config_data_path)
        self._config = {}
        self._bcdb_instances = {}

    def destroy_all(self):
        """
        destroy all remembered BCDB's
        SUPER DANGEROUS
        all data will be lost
        :return:
        """
        for item in self.instances:
            item.destroy()
        for key in j.core.db.keys("bcdb:*"):
            j.core.db.delete(key)

    def get(self, name, storclient=None, reset=False, if_not_exist_die=False):
        """
        will create a new one or an existing one if it exists
        :param name:
        :param storclient:
        :param reset: means do not use an existing one
        :param if_not_exist_die, if True then will die if the instance does not exist yet
        :return:
        """
        if reset:
            if name in self._bcdb_instances:
                self._bcdb_instances.pop(name)
            if name in self._config:
                self._config.pop(name)

        data = {}
        if name in self._bcdb_instances:
            return self._bcdb_instances[name]
        elif name in self._config:
            data = self._config[name]
            if data["type"] == "zdb":
                if "admin" in data:
                    if data["admin"]:
                        raise RuntimeError("can only use ZDB connection which is not admin")
                    data.pop("admin")
                storclient = j.clients.zdb.client_get(**data)
            if data["type"] == "rdb":
                storclient = j.clients.rdb.client_get(**data)
            else:
                storclient = None
        elif if_not_exist_die:
            raise RuntimeError("did not find bcdb with name:%s" % name)

        self._log_debug("new bcdb:%s" % name)
        if storclient != None and j.data.types.string.check(storclient):
            raise RuntimeError("storclient cannot be str")

        if not name in self._config:
            if storclient:
                if storclient.type == "RDB":
                    data["nsname"] = storclient.nsname
                    data["type"] = "rdb"
                    data["redisconfig_name"] = storclient._redis.redisconfig_name
                else:
                    data["nsname"] = storclient.nsname
                    data["admin"] = storclient.admin
                    data["addr"] = storclient.addr
                    data["port"] = storclient.port
                    data["mode"] = storclient.mode
                    data["secret"] = storclient.secret
                    data["type"] = "zdb"
            else:
                data["nsname"] = name
                data["type"] = "sqlite"

            self._config[name] = data
            self._config_write()

        self._bcdb_instances[name] = BCDB(storclient=storclient, name=name, reset=reset)
        return self._bcdb_instances[name]

    def _config_write(self):
        data = j.data.serializers.msgpack.dumps(self._config)
        data_encrypted = j.data.nacl.default.encryptSymmetric(data)
        j.sal.fs.writeFile(self._config_data_path, data_encrypted)

    def new(self, name, storclient=None):
        """
        create a new instance (can also do this using self.new(...))
        :param name:
        :param storclient: optional
        :return:
        """
        return self.get(name=name, storclient=storclient)

    # def redis_server_start(
    #     self,
    #     name="test",
    #     reset=False,
    #     ipaddr="localhost",
    #     port=6380,
    #     background=False,
    #     secret="123456",
    #     bcdbname="test",
    # ):
    #
    #     """
    #     start a redis server on port 6380 on localhost only
    #
    #     you need to feed it with schema's
    #
    #     if zdbclient_addr is None, will use sqlite embedded backend
    #
    #     trick: use RDM to investigate (Redis Desktop Manager) to investigate DB.
    #
    #     kosmos "j.data.bcdb.redis_server_start(background=True)"
    #
    #     kosmos "j.data.bcdb.redis_server_start(background=False,bcdbname="test)"
    #
    #
    #     :return:
    #     """
    #
    #     if background:
    #
    #         args = 'ipaddr="%s", ' % ipaddr
    #         args += 'name="%s", ' % name
    #         args += "port=%s, " % port
    #         args += 'secret="%s", ' % secret
    #         args += 'bcdbname="%s", ' % bcdbname
    #
    #         cmd = "kosmos 'j.data.bcdb.redis_server_start(%s)'" % args
    #
    #         cmdcmd = j.servers.startupcmd.get(name="bcdbredis_%s" % port, cmd=cmd, ports=[port])
    #
    #         cmdcmd.start(reset=reset)
    #
    #         j.sal.nettools.waitConnectionTest(ipaddr=ipaddr, port=port, timeoutTotal=5)
    #         r = j.clients.redis.get(ipaddr=ipaddr, port=port, password=secret)
    #         assert r.ping()
    #
    #     else:
    #         bcdb = self.get(name=bcdbname)
    #         bcdb.redis_server_start(port=port)

    @property
    def _code_generation_dir(self):
        if not self._code_generation_dir_:
            path = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "models")
            j.sal.fs.createDir(path)
            if path not in sys.path:
                sys.path.append(path)
            j.sal.fs.touch(j.sal.fs.joinPaths(path, "__init__.py"))
            self._log_debug("codegendir:%s" % path)
            self._code_generation_dir_ = path
        return self._code_generation_dir_

    def _load_test_model(self, reset=True, type="zdb", schema=None):

        if not schema:
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

        type = type.lower()

        if type == "rdb":
            storclient = j.clients.rdb.client_get()  # will be to core redis
            bcdb = j.data.bcdb.get(name="test", storclient=storclient, reset=reset)

        elif type == "sqlite":
            bcdb = j.data.bcdb.get(name="test", storclient=None, reset=reset)
            bcdb2 = j.data.bcdb.bcdb_instances["test"]
            assert bcdb2.storclient == None
        elif type == "zdb":
            storclient_admin = j.servers.zdb.start_test_instance(destroydata=reset)
            assert storclient_admin.ping()
            secret = "1234"
            storclient = storclient_admin.namespace_new("test", secret=secret)
            if reset:
                storclient.flush()
            assert storclient.nsinfo["public"] == "no"
            assert storclient.ping()
            bcdb = j.data.bcdb.get(name="test", storclient=storclient, reset=reset)
        else:
            raise RuntimeError("only rdb,zdb,sqlite for stor")

        if reset:
            bcdb.reset()  # empty

        schemaobj = j.data.schema.get_from_text(schema)
        model = bcdb.model_get_from_schema(schemaobj)

        self._log_debug("bcdb already exists")

        if reset:

            if type.lower() in ["zdb"]:
                print(model.storclient.nsinfo["entries"])
                assert model.storclient.nsinfo["entries"] == 1
            else:
                assert len(model.find()) == 0

        return bcdb, model

    def _instance_names(self, prefix=None):
        items = []
        # items = [key for key in self.__dict__.keys() if not key.startswith("_")]
        for bcdb in self.instances:
            items.append(bcdb.name)
        items.sort()
        # print(items)
        return items

    def __getattr__(self, name):
        # if private then just return
        if name.startswith("_") or name in self._methods() or name in self._properties():
            return self.__getattribute__(name)
        # else see if we can from the factory find the child object
        r = self.get(name=name)
        # if none means does not exist yet will have to create a new one
        if r is None:
            r = self.new(name=name)
        return r

    def __setattr__(self, key, value):
        if key in ["system", "test"]:
            raise RuntimeError("no system or test allowed")
        self.__dict__[key] = value

    def __str__(self):

        out = "## {GRAY}BCDBS: {BLUE}\n\n"

        for bcdb in self.instances:
            out += " = %s" % bcdb.name

        out += "{RESET}"
        out = j.core.tools.text_replace(out)
        print(out)
        # TODO: *1 dirty hack, the ansi codes are not printed, need to check why
        return ""

    __repr__ = __str__

    def test(self, name=""):
        """
        following will run all tests

        kosmos 'j.data.bcdb.test()'


        """

        self._test_run(name=name)

        j.servers.zdb.stop()
        redis = j.tools.tmux.cmd_get("bcdbredis_6380")
        redis.stop()
        self._log_info("All TESTS DONE")
        return "OK"
