from pyblake2 import blake2b
from Jumpscale import j


import struct
from .BCDBDecorator import *

JSBASE = j.application.JSBaseClass


class BCDBModel(j.application.JSBaseClass):
    def __init__(
        self,
        bcdb,
        schema=None,
        url=None,
        cache_expiration=3600,
        custom=False,
        reset=False,
    ):
        """

        delivers interface how to deal with data in 1 schema

        for query example see http://docs.peewee-orm.com/en/latest/peewee/query_examples.html

        e.g.
        ```
        query = self.index.name.select().where(index.cost > 0)
        for item in self.select(query):
            print(item.name)
        ```
        """

        JSBASE.__init__(self)

        self._kosmosinstance = None

        if bcdb is None:
            raise RuntimeError("bcdb should be set")

        self.bcdb = bcdb
        self.__redis_prefix = None
        self.cache_expiration = cache_expiration

        self.schema = schema

        self.zdbclient = bcdb.zdbclient

        if self.zdbclient:
            # is unique id for a bcdbmodel (unique per zdbclient !)
            self.key = "%s_%s" % (self.zdbclient.nsname, self.schema.url)
        else:
            self.key = self.schema.url
        self.key = self.key.replace(".", "_")

        self.readonly = False

        self.autosave = (
            False
        )  # if set it will make sure data is automatically set from object

        #

        self._triggers = []

        self.custom = custom
        self._init_()
        if reset:
            self.reset()

    def _init_(self):

        self._data_dir = j.sal.fs.joinPaths(self.bcdb._data_dir, self.key)
        j.sal.fs.createDir(self._data_dir)

        if self.cache_expiration > 0:
            self.obj_cache = {}
        else:
            self.obj_cache = None

        self._ids_file_path = "%s/ids.data" % (self._data_dir)

        if (
            not j.sal.fs.exists(self._ids_file_path)
            or j.sal.fs.fileSize(self._ids_file_path) == 0
        ):
            j.sal.fs.touch(self._ids_file_path)
            self._ids_last = 0
        else:
            llen = j.sal.fs.fileSize(self._ids_file_path)
            # make sure the len is multiplication of 4 bytes
            assert float(llen / 4) == llen / 4
            f = open(self._ids_file_path, "rb")
            f.seek(llen - 4, 0)
            bindata = f.read(4)
            self._ids_last = struct.unpack(b"<I", bindata)[0]

        self.schema = self.bcdb.meta.schema_set(self.schema)

        # load all objects in redis
        for obj in self.get_all():
            self._index_key_set("name", obj.name, obj.id)
        self._init_index()  # goal is to be overruled by users

    def trigger_add(self, method):
        """
        see docs/baseclasses/data_mgmt_on_obj.md

        :param method:
        :return:
        """
        if method not in self._triggers:
            self._triggers.append(method)

    def triggers_call(self, obj, action=None, propertyname=None):
        """
        will go over all triggers and call them with arguments given
        see docs/baseclasses/data_mgmt_on_obj.md

        """
        model = self
        kosmosinstance = self._kosmosinstance
        for method in self._triggers:
            method(
                model,
                obj,
                kosmosinstance=kosmosinstance,
                action=action,
                propertyname=propertyname,
            )

    def cache_reset(self):
        self.obj_cache = {}

    @property
    def _redis_prefix(self):
        """
        keep a name to id mapping in the redis, that way we have a short name for the hset for the keys
        :return:
        """
        if self.__redis_prefix is None:
            self.__redis_prefix = self.bcdb._hset_index_key_get(self.schema)
        return self.__redis_prefix

    @queue_method
    def index_ready(self):
        """
        doesn't do much, just makes sure that we wait that queue has been processed upto this point
        :return:
        """
        return True

    def stop(self):
        """
        stops the data processor
        """
        if self.bcdb.dataprocessor_greenlet is None:
            # is already stopped
            return True
        event = Event()
        j.data.bcdb.latest.queue.put((None, ["STOP"], {}, event, None))

        event.wait(1000.0)  # will wait for processing
        if self.bcdb._sqlclient is not None:
            self.bcdb.sqlclient.close()
            self.bcdb._sqlclient = None

        self._log_info("DATAPROCESSOR & SQLITE STOPPED OK")
        return True

    # def start(self):
    #     if self.dataprocessor_greenlet is None:
    #         self.bcdb.dataprocessor_start()
    #     self.index_ready() #will only return when dataprocessor working

    @queue_method
    def index_rebuild(self):
        self.stop()
        self.index_destroy()
        self._log_warning("will rebuild index for:%s" % self)
        for obj in self.iterate(die=False):
            self._set(obj, store=False)

    @queue_method
    def delete(self, obj):
        if not hasattr(obj, "_JSOBJ"):
            obj = self.get(obj)
        self.triggers_call(obj=obj, action="delete")
        if obj.id is not None:
            self.index_keys_delete(obj)
            self._delete2(obj.id)
            if obj.id in self.obj_cache:
                self.obj_cache.pop(obj.id)
            if self.index:
                self.index_delete(obj.id)
            self.id_delete(obj.id)

    def _delete2(self, obj_id):
        if not self.zdbclient:
            self.bcdb.sqlclient.delete(key=obj_id)
        else:
            self.zdbclient.delete(obj_id)

    def check(self, obj):
        if not hasattr(obj, "_JSOBJ"):
            raise RuntimeError("argument needs to be a bcdb obj")

    @queue_method
    def set_dynamic(self, data, obj_id=None):
        """
        if string -> will consider to be json
        if binary -> will consider data for capnp
        if obj -> will check of JSOBJ
        if ddict will put inside JSOBJ
        """
        if j.data.types.string.check(data):
            data = j.data.serializers.json.loads(data)
            if obj_id == None and "id" in data:
                obj_id = data["id"]
            obj = self.schema.get(data)
        elif j.data.types.bytes.check(data):
            obj = self.schema.get(capnpbin=data)
            if obj_id is None:
                raise RuntimeError("objid cannot be None")
        elif getattr(data, "_JSOBJ", None):
            obj = data
            if obj_id is None and obj.id is not None:
                obj_id = obj.id
        elif j.data.types.dict.check(data):
            if obj_id == None and "id" in data:
                obj_id = data["id"]
            obj = self.schema.get(data)
        else:
            raise RuntimeError(
                "Cannot find data type, str,bin,obj or ddict is only supported"
            )
        obj.id = obj_id  # do not forget
        return self._set(obj)

    def _index_key_set(self, property_name, val, obj_id):
        """

        :param property_name: property name to index
        :param val: the value of the property which we want to index
        :param obj_id: id of the obj
        :return:
        """

        key = "%s__%s" % (property_name, val)
        ids = self._index_key_getids(key)
        if obj_id is None:
            raise RuntimeError("id cannot be None")
        if obj_id not in ids:
            ids.append(obj_id)
        data = j.data.serializers.msgpack.dumps(ids)
        hash = self._index_key_redis_get(key)
        self._log_debug("set key:%s (id:%s)" % (key, obj_id))
        j.clients.credis_core.hset(
            self._redis_prefix + b":" + hash[0:2], hash[2:], data
        )

    def _index_key_delete(self, property_name, val, obj_id):

        key = "%s__%s" % (property_name, val)
        ids = self._index_key_getids(key)
        if obj_id is None:
            raise RuntimeError("id cannot be None")
        if obj_id in ids:
            ids.pop(ids.index(obj_id))
        hash = self._index_key_redis_get(key)
        if ids == []:
            j.clients.credis_core.hdel(self._redis_prefix + b":" + hash[0:2], hash[2:])
        else:
            data = j.data.serializers.msgpack.dumps(ids)
            hash = self._index_key_redis_get(key)
            self._log_debug("set key:%s (id:%s)" % (key, obj_id))
            j.clients.credis_core.hdel(
                self._redis_prefix + b":" + hash[0:2], hash[2:], data
            )

    def _index_keys_destroy(self):
        for key in j.clients.credis_core.keys(self._redis_prefix + b"*"):
            j.clients.credis_core.delete(key)

    def _index_key_getids(self, key):
        hash = self._index_key_redis_get(key)

        r = j.clients.credis_core.hget(self._redis_prefix + b":" + hash[0:2], hash[2:])
        if r is not None:
            # means there is already one
            self._log_debug("get key(exists):%s" % key)
            ids = j.data.serializers.msgpack.loads(r)

        else:
            self._log_debug("get key(new):%s" % key)
            ids = []
        return ids

    def get_from_keys(self, delete_if_not_found=False, **args):
        """
        is a the retrieval part of a very fast indexing system
        e.g.
        self.get_from_keys(name="myname")
        :return:
        """
        if len(args.keys()) == 0:
            raise RuntimeError("get from keys need arguments")
        ids_prev = []
        ids = []
        for propname, val in args.items():
            key = "%s__%s" % (propname, val)
            ids = self._index_key_getids(key)
            if ids_prev != []:
                ids = [x for x in ids if x in ids_prev]
            ids_prev = ids

        res = []
        for id_ in ids:
            res2 = self.get(id_, die=None)
            if res2 is None:
                if delete_if_not_found:
                    for key, val in args.items():
                        self._index_key_delete(key, val, id_)
                else:
                    raise RuntimeError(
                        "backend data store out of sync with key index in redis (redis has it, backend not)"
                    )
            res.append(res2)

        return res

    def get_id_from_key(self, key):
        """

        :param sid: schema id
        :param key: key used to store
        :return:
        """
        ids = self._index_key_getids(key)
        if len(ids) == 1:
            return ids[0]
        elif len(ids) > 1:
            # need to fetch obj to see what is alike
            j.shell()

    def _index_key_redis_get(self, key):
        """
        returns 10 bytes as key (non HR readable)
        :param key:
        :return:
        """
        # schema id needs to be in to make sure itd different key per schema
        key2 = j.core.text.strip_to_ascii_dense(key) + str(self.schema.sid)
        # can do 900k per second
        hash = blake2b(str(key2).encode(), digest_size=10).digest()
        return hash

    @queue_method_results
    def _set(self, obj, index=True, store=True):
        """
        :param obj
        :return: obj
        """
        self.check(obj)

        if store:

            # later:
            if obj.acl_id is None:
                obj.acl_id = 0

            if obj._acl is not None:
                if obj.acl.id is None:
                    # need to save the acl
                    obj.acl.save()
                else:
                    acl2 = obj.model.bcdb.acl.get(obj.acl.id)
                    if acl2 is None:
                        # means is not in db
                        obj.acl.save()
                    else:
                        if obj.acl.hash != acl2.hash:
                            obj.acl.id = None
                            obj.acl.save()  # means there is acl but not same as in DB, need to save
                            if obj.acl.readonly:
                                obj.acl.readonly = True
                            self._obj_cache_reset()
                obj.acl_id = obj.acl.id

            try:
                bdata = obj._data
            except Exception as e:
                if str(e).find("has no such member") != -1:
                    msg = str(e).split("no such member", 1)[1].split("stack:")
                    raise RuntimeError("Could not serialize capnnp message:%s" % msg)
                else:
                    raise e

            bdata_encrypted = j.data.nacl.default.encryptSymmetric(bdata)

            l = [self.schema.sid, obj.acl_id, bdata_encrypted]
            data = j.data.serializers.msgpack.dumps(l)

            self.triggers_call(obj, action="set_pre")

            # PUT DATA IN DB
            if obj.id is None:
                # means a new one
                if not self.zdbclient:
                    obj.id = self.bcdb.sqlclient.set(key=None, val=data)
                else:
                    obj.id = self.zdbclient.set(data)
                if self.readonly:
                    obj.readonly = True
                self._log_debug("NEW:\n%s" % obj)
            else:
                if not self.zdbclient:
                    self.bcdb.sqlclient.set(key=obj.id, val=data)
                else:
                    try:
                        self.zdbclient.set(data, key=obj.id)
                    except Exception as e:
                        if str(e).find("only update authorized") != -1:
                            raise RuntimeError(
                                "cannot update object:%s\n with id:%s, does not exist"
                                % (obj, obj.id)
                            )
                        raise

        if index:
            self.index_set(obj)
            self.index_keys_set(obj)

            if obj.id > self._ids_last:
                bin_id = struct.pack("<I", obj.id)
                j.sal.fs.writeFile(self._ids_file_path, bin_id, append=True)
                self._ids_last = obj.id

        self.triggers_call(obj=obj, action="set_post")

        return obj

    @property
    def id_iterator(self):
        """
        ```
        for obj_id in m.id_iterator:
            o=m.get(obj_id)
        ```
        :return:
        """
        # print("idspath:%s"%self._ids_file_path)
        with open(self._ids_file_path, "rb") as f:
            while True:
                chunk = f.read(4)
                if chunk:
                    obj_id = struct.unpack("<I", chunk)[0]
                    yield obj_id
                else:
                    break

    def id_delete(self, id):
        out = b""
        for id_ in self.id_iterator:
            if id_ != id:
                out += struct.pack("<I", id_)
        j.sal.fs.writeFile(self._ids_file_path, out)

    def _dict_process_out(self, ddict):
        """
        whenever dict is needed this method will be called before returning
        :param ddict:
        :return:
        """
        return ddict

    def _dict_process_in(self, ddict):
        """
        when data is inserted back into object
        :param ddict:
        :return:
        """
        return ddict

    def new(self, data=None, capnpbin=None):
        if data:
            data = self._dict_process_in(data)
        if data or capnpbin:
            obj = self.schema.get(data=data, capnpbin=capnpbin, model=self)
        else:
            obj = self.schema.new()
            obj._model = self
        obj = self._methods_add(obj)
        self.triggers_call(obj=obj, action="new")
        return obj

    def _methods_add(self, obj):
        return obj

    def index_set(self, obj):
        pass

    def index_keys_set(self, obj):
        pass

    def index_destroy(self):
        self._index_keys_destroy()

    def index_delete(self, obj):
        if self.index:
            if not j.data.types.int.check(obj):
                obj = obj.id
            self.index.delete_by_id(obj)

    @queue_method_results
    def get(self, obj_id, return_as_capnp=False, usecache=True, die=True):
        """
        @PARAM id is an int or a key
        @PARAM capnp if true will return data as capnp binary object,
               no hook will be done !
        @RETURN obj    (.index is in obj)
        """

        if obj_id in [None, 0, "0", b"0"]:
            raise RuntimeError("id cannot be None or 0")

        if self.obj_cache is not None and usecache:
            # print("use cache")
            if obj_id in self.obj_cache:
                epoch, obj = self.obj_cache[obj_id]
                if j.data.time.epoch > self._cache_expiration + epoch:
                    self.obj_cache.pop(obj_id)
                    # print("dirty cache")
                else:
                    # print("cache hit")
                    return obj

        if not self.zdbclient:
            data = self.bcdb.sqlclient.get(key=obj_id)
        else:
            data = self.zdbclient.get(obj_id)

        if not data:
            if die:
                raise RuntimeError("could not find obj with id:%s" % obj_id)
            else:
                return None

        obj = self.bcdb._unserialize(
            obj_id, data, return_as_capnp=return_as_capnp, model=self
        )
        # self.obj_cache[obj_id] = (j.data.time.epoch, obj)  #FOR NOW NO CACHE, UNSAFE

        self.triggers_call(obj=obj, action="get")

        return obj

    def delete_all(self):
        for obj_id in self.id_iterator:
            self.delete(obj_id)

    def reset(self):
        self._log_warning("reset:%s" % self.key)
        if self.zdbclient:
            self.delete_all()  # only for zdb relevant

        # now need to remove tables from index
        self.index_destroy()

        self.stop()
        j.sal.fs.remove(self._data_dir)

        tofind = self.bcdb._hset_index_key_get(self.schema) + b":*"

        for key in j.clients.credis_core.keys(tofind):
            j.clients.credis_core.delete(key)

        self._init_()

    def iterate(self, die=True):
        """
        walk over objects which are of type of this model
        """
        for obj_id in self.id_iterator:
            try:
                o = self.get(obj_id)
            except Exception as e:
                if str(e).find("could not find obj") != -1:
                    self._log_warning(
                        "warning: could not find object with id:%s in %s"
                        % (obj_id, self)
                    )
                    continue
                else:
                    raise e
            yield o

    def get_all(self):
        res = []
        for obj in self.iterate():
            if obj is None:
                raise RuntimeError("iterate should not return None, ever")
            res.append(obj)
        return res

    def _init_index(self):
        pass

    def notify_new(self, obj):
        return

    def __str__(self):
        out = "model:%s\n" % self.schema.url
        # out += j.core.text.prefix("    ", self.schema.text)
        return out

    __repr__ = __str__
