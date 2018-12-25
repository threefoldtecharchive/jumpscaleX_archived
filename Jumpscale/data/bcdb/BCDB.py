# from importlib import import_module

import gevent
from Jumpscale.clients.zdb.ZDBClientBase import ZDBClientBase
from gevent import queue
from .BCDBModel import BCDBModel
from .BCDBMeta import BCDBMeta
from .BCDBDecorator import *
from .RedisServer import RedisServer
from .BCDBIndexMeta import BCDBIndexMeta
from Jumpscale import j
import sys
from .DBSQLite import DBSQLite

JSBASE = j.application.JSBaseClass


class BCDB(j.application.JSBaseClass):

    def __init__(self, name=None, zdbclient=None, reset=False):
        """
        :param name: name for the BCDB
        :param zdbclient: if zdbclient == None then will only use sqlite db
        """
        JSBASE.__init__(self)

        if name is None:
            raise RuntimeError("name needs to be specified")

        if zdbclient is not None:
            if not isinstance(zdbclient, ZDBClientBase):
                raise RuntimeError(
                    "zdbclient needs to be type: clients.zdb.ZDBClientBase")

        self.name = name
        self._sqlclient = None
        self._data_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, "bcdb", self.name)

        self._need_to_reset = reset
        j.data.bcdb.bcdb_instances[self.name] = self
        j.data.bcdb.latest = self

        if not j.data.types.string.check(self.name):
            raise RuntimeError("name needs to be string")

        self.zdbclient = zdbclient

        self.dataprocessor_greenlet = None

        self.meta = BCDBMeta(self)
        self._logger_enable()

        self._init_(reset=reset, stop=False)

    @property
    def sqlclient(self):
        if self._sqlclient is None:
            self._sqlclient = DBSQLite(self)
        return self._sqlclient

    def _init_(self, stop=True, reset=False):

        if stop:
            self.stop()

        self._sqlclient = None

        self.dataprocessor_start()

        self.acl = None
        self.user = None
        self.group = None

        self.models = {}

        self._index_schema_class_cache = {}  # cache for the index classes

        if reset:
            self._reset()

        j.sal.fs.createDir(self._data_dir)

        # needed for async processing
        self.results = {}
        self.results_id = 0

        # need to do this to make sure we load the classes from scratch
        for item in ["ACL", "USER", "GROUP"]:
            key = "Jumpscale.data.bcdb.models_system.%s" % item
            if key in sys.modules:
                sys.modules.pop(key)

        from .models_system.ACL import ACL
        from .models_system.USER import USER
        from .models_system.GROUP import GROUP

        self.acl = self.model_add(ACL())
        self.user = self.model_add(USER())
        self.group = self.model_add(GROUP())

        self._logger_enable()
        self._logger.info("BCDB INIT DONE:%s" % self.name)

    def redis_server_start(self, port=6380, secret="123456"):

        self.redis_server = RedisServer(bcdb=self, port=port, secret=secret)
        self.redis_server.init()
        self.redis_server.start()

    def _data_process(self):
        # needs gevent loop to process incoming data
        self._logger.info("DATAPROCESSOR STARTS")
        while True:
            method, args, kwargs, event, returnid = self.queue.get()
            if args == ["STOP"]:
                break
            else:
                res = method(*args, **kwargs)
                if returnid:
                    self.results[returnid] = res
                event.set()
        self.dataprocessor_greenlet = None
        event.set()
        self._logger.warning("DATAPROCESSOR STOPS")

    def dataprocessor_start(self):
        """
        will start a gevent loop and process the data in a greenlet

        this allows us to make sure there will be no race conditions when gevent used or when subprocess
        main issue is the way how we populate the sqlite db (if there is any)

        :return:
        """
        if self.dataprocessor_greenlet is None:
            self.queue = gevent.queue.Queue()
            self.dataprocessor_greenlet = gevent.spawn(self._data_process)
            self.dataprocessor_state = "RUNNING"

    def reset(self):
        """
        resets data & index
        :return:
        """
        self._init_(stop=True, reset=True)


    def _hset_index_key_get(self,schema):
        if not isinstance(schema,j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: SCHEMA_CLASS")

        key=[self.name,schema.url]
        r = j.clients.credis_core.get("bcdb.schema.instances")
        if r is None:
            data={}
            data["lastid"]=0
        else:
            data = j.data.serializers.json.loads(r)
        if self.name not in data:
            data[self.name]={}
        if schema.url not in data[self.name]:
            data["lastid"]=data["lastid"]+1
            data[self.name][schema.url]=data["lastid"]

            bindata = j.data.serializers.json.dumps(data)
            j.clients.credis_core.set("bcdb.instances",bindata)

        return b"O:"+str(data[self.name][schema.url]).encode()


    def _hset_index_key_delete(self):
        r = j.clients.credis_core.get("bcdb.instances")
        if r is None:
            return
        data = j.data.serializers.json.loads(r)
        if self.name in data:
            for url,key_id in data[self.name].items():
                tofind=b"O:"+str(key_id).encode()+b":*"
                for key in j.clients.credis_core.keys(tofind):
                    print("HKEY DELETE:%s"%key)
                    j.clients.credis_core.delete(key)

        j.shell()


    def _reset(self):

        if self.zdbclient:
            self.zdbclient.flush(meta=self.meta)  # new flush command

        for key, m in self.models.items():
            m.reset()

        if self._sqlclient is not None:
            self.sqlclient.close()
            self._sqlclient = None

        # need to clean redis
        self._hset_index_key_delete()

        j.sal.fs.remove(self._data_dir)

    def stop(self):
        self._logger.info("STOP BCDB")
        if self.dataprocessor_greenlet is not None:
            self.dataprocessor_greenlet.kill()
        self.dataprocessor_greenlet = None

    def index_rebuild(self):

        self._logger.warning("REBUILD INDEX")
        self.meta.reset()
        for url, model in self.models.items():
            if model.bcdb != self:
                raise RuntimeError("bcdb on model needs to be same as myself")
            model.index_rebuild()
            self.meta.schema_set(model.schema)

    def cache_flush(self):
        # put all caches on zero
        for model in self.models.values():
            if model.cache_expiration > 0:
                model.obj_cache = {}
            else:
                model.obj_cache = None
            model._init()

    def model_get(self, url):
        # url = j.core.text.strip_to_ascii_dense(url).replace(".", "_")
        if url not in self.models:
            m = self.meta.model_get_from_url(url)
            raise RuntimeError("could not find model for url:%s" % url)
        return self.models[url]

    def model_add(self, model):
        """

        :param model: is the model object  : inherits of self.MODEL_CLASS
        :return:
        """
        if not isinstance(model, self._BCDBModelClass):
            raise RuntimeError("model needs to be of type:%s" %
                               self._BCDBModelClass)
        self.models[model.schema.url] = model
        return self.models[model.schema.url]

    def model_get_from_schema(self, schema, dest=""):
        """
        :param schema: is schema as text or as schema obj
        :param reload: will reload template
        :param overwrite: will overwrite the resulting file even if it already exists
        :return:
        """

        if j.data.types.str.check(schema):
            schema_text = schema
            schema = j.data.schema.get(schema_text)
            self._logger.debug(
                "model get from schema:%s, original was text." % schema.url)
        else:
            self._logger.debug("model get from schema:%s" % schema.url)
            if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
                raise RuntimeError(
                    "schema needs to be of type: j.data.schema.SCHEMA_CLASS")
            schema_text = schema.text

        r = self.meta.model_get_from_md5(
            j.data.hash.md5_string(schema_text), die=False)
        if r is not None:
            return r

        tpath = "%s/templates/BCDBModelClass.py" % j.data.bcdb._path
        objForHash = schema_text
        myclass = j.tools.jinja2.code_python_render(path=tpath,
                                                    reload=False, dest=dest, objForHash=objForHash,
                                                    schema_text=schema_text, bcdb=self, schema=schema,
                                                    overwrite=False)

        model = myclass(reset=self._need_to_reset, bcdb=self, schema=schema)
        self.models[schema.url] = model

        return self.model_get(schema.url)

    def _BCDBModelIndexClass_generate(self, schema, path_parent=None):
        """

        :param schema: is schema object j.data.schema... or text
        :return: class of the model which is used for indexing

        """
        self._logger.debug("generate schema:%s" % schema.url)
        if path_parent:
            name = j.sal.fs.getBaseName(path_parent)[:-3]
            dir_path = j.sal.fs.getDirName(path_parent)
            dest = "%s/%s_index.py" % (dir_path, name)

        if j.data.types.str.check(schema):
            schema = j.data.schema.get(schema)

        elif not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError(
                "schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        if schema.key not in self._index_schema_class_cache:

            # model with info to generate
            imodel = BCDBIndexMeta(schema=schema)
            imodel.include_schema = True
            tpath = "%s/templates/BCDBModelIndexClass.py" % j.data.bcdb._path
            myclass = j.tools.jinja2.code_python_render(path=tpath,
                                                        reload=True, dest=dest,
                                                        schema=schema, bcdb=self, index=imodel)

            self._index_schema_class_cache[schema.key] = myclass

        return self._index_schema_class_cache[schema.key]

    @property
    def _BCDBModelClass(self):
        return BCDBModel

    def model_get_from_file(self, path):
        """
        add model to BCDB
        is path to python file which represents the model

        """
        self._logger.debug("model get from file:%s" % path)
        obj_key = j.sal.fs.getBaseName(path)[:-3]
        cl = j.tools.loader.load(obj_key=obj_key, path=path, reload=False)
        model = cl()
        self.models[model.schema.url] = model
        return model

    def models_add(self, path, overwrite=True):
        """
        will walk over directory and each class needs to be a model
        when overwrite used it will overwrite the generated models (careful)
        :param path:
        :return: None
        """
        self._logger.debug("models_add:%s" % path)

        if not j.sal.fs.isDir(path):
            raise RuntimeError(
                "path: %s needs to be dir, to load models from" % path)

        pyfiles_base = []
        for fpath in j.sal.fs.listFilesInDir(path, recursive=True, filter="*.py", followSymlinks=True):
            pyfile_base = j.tools.loader._basename(fpath)
            if pyfile_base.find("_index") == -1:
                pyfiles_base.append(pyfile_base)

        tocheck = j.sal.fs.listFilesInDir(
            path, recursive=True, filter="*.toml", followSymlinks=True)
        for schemapath in tocheck:

            bname = j.sal.fs.getBaseName(schemapath)[:-5]
            if bname.startswith("_"):
                continue

            schema_text = j.sal.fs.readFile(schemapath)
            schema = j.data.schema.get(schema_text)
            toml_path = "%s.toml" % (schema.key)
            if j.sal.fs.getBaseName(schemapath) != toml_path:
                toml_path = "%s/%s.toml" % (
                    j.sal.fs.getDirName(schemapath), schema.key)
                j.sal.fs.renameFile(schemapath, toml_path)
                schemapath = toml_path

            dest = "%s/%s.py" % (path, bname)

            self.model_get_from_schema(schema=schema, dest=dest)

        for pyfile_base in pyfiles_base:
            if pyfile_base.startswith("_"):
                continue
            path2 = "%s/%s.py" % (path, pyfile_base)
            self.model_get_from_file(path2)

    def _unserialize(self, id, data, return_as_capnp=False, model=None):

        res = j.data.serializers.msgpack.loads(data)

        if len(res) == 3:
            schema_id, acl_id, bdata_encrypted = res
            if model:
                if schema_id != model.schema.sid:
                    model =self.meta.model_get_from_id(schema_id,bcdb=self)
            else:
                model = self.meta.model_get_from_id(schema_id, bcdb=self)
        else:
            raise RuntimeError("not supported format in table yet")

        bdata = j.data.nacl.default.decryptSymmetric(bdata_encrypted)

        if return_as_capnp:
            return bdata
        else:
            obj = model.schema.get(capnpbin=bdata)
            obj.id = id
            obj.acl_id = acl_id
            obj.model = model
            if model.write_once:
                obj.readonly = True  # means we fetched from DB, we need to make sure cannot be changed
            return obj

    def obj_get(self, id):

        data = self.zdbclient.get(id)
        if data is None:
            return None
        return self._unserialize(id, data)

    def iterate(self, key_start=None, reverse=False, keyonly=False):
        """
        walk over all the namespace and yield each object in the database

        :param key_start: if specified start to walk from that key instead of the first one, defaults to None
        :param key_start: str, optional
        :param reverse: decide how to walk the namespace
                if False, walk from older to newer keys
                if True walk from newer to older keys
                defaults to False
        :param reverse: bool, optional
        :param keyonly: [description], defaults to False
        :param keyonly: bool, optional
        :raises e: [description]
        """
        if self.zdbclient:
            db = self.zdbclient
            for key, data in db.iterate(key_start=key_start, reverse=reverse, keyonly=keyonly):
                if key == 0:  # skip first metadata entry
                    continue
                if keyonly:
                    yield key
                elif data:
                    obj = self._unserialize(key, data)
                else:
                    obj = ""

                yield obj
        else:
            for key, data in self.sqlclient.iterate():
                if key == 0:  # skip first metadata entry
                    continue
                obj = self._unserialize(key, data)
                yield obj

    def get_all(self):
        return [obj for obj in self.iterate()]
