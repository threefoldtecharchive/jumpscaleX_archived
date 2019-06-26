from Jumpscale import j

from .BCDB import BCDB
from .BCDBModel import BCDBModel
from .BCDBVFS import BCDBVFS
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

        self._BCDBModelClass = BCDBModel  # j.data.bcdb._BCDBModelClass

        self._load()

    def _load(self):

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
        bcdb = j.data.bcdb.new(name="testbcdb")
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
            if self.exists(name):
                bcdb = self.get(name)
                res.append(bcdb)
            # SHOULD EXIST IN FIRST PLACE NO NEED TO DO NEW
            # else:
            #     if data["type"] == "zdb":
            #         storclient = j.clients.zdb.client_get(**data)
            #         bcdb = self.new(name=name, storclient=storclient)
            #     elif data["type"] == "rdb":
            #         storclient = j.clients.rdb.client_get(**data)
            #         bcdb = self.new(name=name, storclient=storclient)
            #     else:
            #         bcdb = self.new(name=name)
            #     res.append(bcdb)

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
        for key in j.core.db.keys("bcdb:*"):
            j.core.db.delete(key)
        for item in self.instances:
            item.destroy()

    def exists(self, name):
        b = self._get(name=name, reset=False, if_not_exist_die=False)
        if b:
            return True
        return False

    def get(self, name, reset=False):
        """
        will create a new one or an existing one if it exists
        :param name:
        :param reset: will remove the data
        :return:
        """
        return self._get(name=name, reset=reset)

    def _get_vfs(self):
        return BCDBVFS(self._bcdb_instances)

    def _get(self, name, reset=False, if_not_exist_die=True):
        data = {}
        if name in self._bcdb_instances:
            bcdb = self._bcdb_instances[name]
            if reset:
                bcdb.reset()
            return bcdb
        elif name in self._config:
            data = self._config[name]
            if data["type"] == "zdb":
                if "admin" in data:
                    if data["admin"]:
                        raise RuntimeError("can only use ZDB connection which is not admin")
                    data.pop("admin")
                storclient = j.clients.zdb.client_get(**data)
            elif data["type"] == "rdb":
                storclient = j.clients.rdb.client_get(**data)
            else:
                storclient = None
        elif if_not_exist_die:
            raise RuntimeError("did not find bcdb with name:%s" % name)
        else:
            return None

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

        self._log_info("new bcdb:%s" % name)
        if name in self._bcdb_instances:  # make sure we don't remember when a new one
            self._bcdb_instances.pop(name)
        if storclient != None and j.data.types.string.check(storclient):
            raise RuntimeError("storclient cannot be str")
        data = {}

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
        self._load()

        bcdb = self.get(name=name)

        if storclient:
            assert bcdb.storclient
            assert bcdb.storclient.type == storclient.type
        return bcdb

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
            bcdb = j.data.bcdb.new(name="test", storclient=storclient)

        elif type == "sqlite":
            bcdb = j.data.bcdb.new(name="test")
            bcdb2 = j.data.bcdb.get("test")
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
            bcdb = j.data.bcdb.new(name="test", storclient=storclient)
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
        if name.startswith("_") or name in self.__names_methods() or name in self.__names_properties():
            return self.__getattribute__(name)
        # else see if we can from the factory find the child object
        r = self.get(name=name)
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

        # j.servers.zdb.stop()
        # redis = j.tools.tmux.cmd_get("bcdbredis_6380")
        # redis.stop()
        self._log_info("All TESTS DONE")
        return "OK"
