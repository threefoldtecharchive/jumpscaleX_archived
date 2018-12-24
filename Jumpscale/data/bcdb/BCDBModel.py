from Jumpscale import j


import struct
from .BCDBDecorator import *
JSBASE = j.application.JSBaseClass

from pyblake2 import blake2b


class BCDBModel(j.builder._BaseClass):
    def __init__(self, bcdb, schema=None,url=None, cache_expiration=3600,custom=False, reset=False):
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

        if bcdb is None:
            raise RuntimeError("bcdb should be set")

        self.bcdb = bcdb
        self.__redis_key = None
        self.cache_expiration = cache_expiration

        self.schema = schema

        self.zdbclient = bcdb.zdbclient

        if self.zdbclient:
            self.key = "%s_%s"%(self.zdbclient.nsname,self.schema.url)  #is unique id for a bcdbmodel (unique per zdbclient !)
        else:
            self.key = self.schema.url
        self.key = self.key.replace(".","_")

        self.write_once = False

        self.autosave = False  # if set it will make sure data is automatically set from object

        self._logger_enable()

        self._modifiers=[]

        self.custom = custom
        self._init_()
        if reset:
            self.reset()


    def _init_(self):

        self._data_dir = j.sal.fs.joinPaths(self.bcdb._data_dir, self.key)
        j.sal.fs.createDir(self._data_dir)

        if self.cache_expiration>0:
            self.obj_cache = {}
        else:
            self.obj_cache = None

        self._ids_file_path = "%s/ids.data"%(self._data_dir)

        if not j.sal.fs.exists(self._ids_file_path) or j.sal.fs.fileSize(self._ids_file_path)==0:
            j.sal.fs.touch(self._ids_file_path )
            self._ids_last = 0
        else:
            llen=j.sal.fs.fileSize(self._ids_file_path)
            assert float(llen/4)==llen/4  #make sure the len is multiplication of 4 bytes
            f = open(self._ids_file_path, 'rb')
            f.seek(llen-4, 0)
            bindata = f.read(4)
            self._ids_last = struct.unpack(b"<I",bindata)[0]

        self.schema = self.bcdb.meta.schema_set(self.schema)

        self._init_index() #goal is to be overruled by users

    def modifier_add(self,method):
        """
        will call the method as follows before doing a set in DB
            method(model,obj)

        :param method:
        :return:
        """
        if method not in self._modifiers:
            self._modifiers.append(method)


    def cache_reset(self):
        self.obj_cache = {}

    @property
    def _redis_key(self):
        """
        keep a name to id mapping in the redis, that way we have a short name for the hset for the keys
        :return:
        """
        if self.__redis_key is None:
            r = j.clients.credis_core.get("bcdb.instances")
            if r is None:
                r = []
            else:
                r = j.data.serializers.msgpack.loads(r)
            if self.key not in r:
                r.append(self.key)
                j.clients.credis_core.set("bcdb.instances",j.data.serializers.msgpack.dumps(r))
            self.__redis_key = b"O:"+str(r.index(self.key)).encode()

        return self.__redis_key


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
            #is already stopped
            return True
        event=Event()
        j.data.bcdb.latest.queue.put((None,["STOP"],{}, event,None))

        event.wait(1000.0) #will wait for processing
        if self.bcdb._sqlclient is not None:
            self.bcdb.sqlclient.close()
            self.bcdb._sqlclient = None

        self._logger.info("DATAPROCESSOR & SQLITE STOPPED OK")
        return True

    # def start(self):
    #     if self.dataprocessor_greenlet is None:
    #         self.bcdb.dataprocessor_start()
    #     self.index_ready() #will only return when dataprocessor working

    @queue_method
    def index_rebuild(self):
        #need to remove index
        self.stop()
        for obj in self.iterate():
            self._set(obj,store=False)

    @queue_method
    def delete(self, obj):
        if hasattr(obj, "_JSOBJ"):
            obj_id = obj.id
        else:
            obj_id = obj

        self._delete2(obj_id)
        if obj_id in self.obj_cache:
            self.obj_cache.pop(obj_id)
        if self.index:
            self.index_delete(obj_id)
        if hasattr(obj, "key"):
            self._delete_key(obj.key,obj_id=obj_id)


    def _delete2(self,obj_id):
        if not self.zdbclient:
            self.bcdb.sqlclient.delete(key=obj_id)
        else:
            return self.zdbclient.delete(obj_id)

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
            raise RuntimeError("Cannot find data type, str,bin,obj or ddict is only supported")
        obj.id = obj_id  # do not forget
        return self._set(obj)

    def _set_key(self,property_name,val,obj_id):
        """

        :param property_name: property name to index
        :param val: the obj
        :param obj_id: id of the obj
        :return:
        """

        key = "%s__%s"%(property_name,val)
        ids = self._get_ids_from_key(key)
        if obj_id is None:
            raise RuntimeError("id cannot be None")
        if obj_id not in ids:
            ids.append(obj_id)
        data = j.data.serializers.msgpack.dumps(ids)
        hash = self._get_redis_key(key)
        self._logger.debug("set key:%s (id:%s)"%(key,obj_id ))
        j.clients.credis_core.hset(self._redis_key+b":"+hash[0:2],hash[2:],data)


    def _delete_key(self,key,obj_id):

        if obj_id is None:
            raise RuntimeError("id cannot be None")
        ids = self._get_ids_from_key(key)
        if obj_id in ids:
            ids.pop(ids.index(obj_id))
        if ids == []:
            j.clients.credis_core.hdel(self._redis_key+b":"+hash[0:2],hash[2:])
        else:
            data = j.data.serializers.msgpack.dumps(ids)
            hash = self._get_redis_key(key)
            self._logger.debug("set key:%s (id:%s)"%(key,obj_id))
            j.clients.credis_core.hset(self._redis_key+b":"+hash[0:2],hash[2:],data)


    def _get_ids_from_key(self,key):
        hash=self._get_redis_key(key)

        r = j.clients.credis_core.hget(self._redis_key+b":"+hash[0:2],hash[2:])
        if r is not None:
            #means there is already one
            self._logger.debug("get key(exists):%s"%key)
            ids = j.data.serializers.msgpack.loads(r)
        else:
            self._logger.debug("get key(new):%s"%key)
            ids = []
        return ids


    def get_from_keys(self, **args):
        """

        e.g.
        self.get_from_keys(name="myname")
        :return:
        """
        if len(args.keys())==0:
            raise RuntimeError("get from keys need arguments")
        ids_prev=[]
        ids=[]
        for propname,val in args.items():
            key = "%s__%s"%(propname,val)
            ids = self._get_ids_from_key(key)
            if ids_prev != []:
                ids = [x for x in ids if x in ids_prev]
            ids_prev = ids

        res = []
        for id_ in ids:
            res2=self.get(id_,die=None)
            if res2 is None:
                raise RuntimeError("backend data store out of sync with key index in redis (redis has it, backend not)")
            res.append(res2)

        return res

    def get_id_from_key(self,key):
        """

        :param sid: schema id
        :param key: key used to store
        :return:
        """
        ids = self._get_ids_from_key(key)
        if len(ids)==1:
            return ids[0]
        elif len(ids)>1:
            #need to fetch obj to see what is alike
            j.shell()

    def _get_redis_key(self,key):
        """
        returns 10 bytes as key (non HR readable)
        :param key:
        :return:
        """
        key2=j.core.text.strip_to_ascii_dense(key)+str(self.schema.sid) #schema id needs to be in to make sure itd different key per schema
        hash=blake2b(str(key2).encode(),digest_size=10).digest() #can do 900k per second
        return hash



    @queue_method_results
    def _set(self, obj, index=True, set_pre=True,store=True):
        """
        :param obj
        :return: obj
        """
        self.check(obj)

        # prepare
        if set_pre:
            store,obj = self._set_pre(obj)

        if store:

            # later:
            if obj.acl_id is None:
                obj.acl_id = 0

            if obj._acl is not None:
                if obj.acl.id is None:
                    #need to save the acl
                    obj.acl.save()
                else:
                    acl2 = obj.model.bcdb.acl.get(obj.acl.id)
                    if acl2 is None:
                        #means is not in db
                        obj.acl.save()
                    else:
                        if obj.acl.hash != acl2.hash:
                            obj.acl.id = None
                            obj.acl.save() #means there is acl but not same as in DB, need to save
                            if obj.acl.write_once:
                                obj.acl.readonly = True
                            self._cache_reset()
                obj.acl_id = obj.acl.id

            bdata = obj._data
            bdata_encrypted = j.data.nacl.default.encryptSymmetric(bdata)

            l = [self.schema.sid, obj.acl_id, bdata_encrypted]
            data = j.data.serializers.msgpack.dumps(l)

            #PUT DATA IN DB
            if obj.id is None:
                # means a new one
                if not self.zdbclient:
                    obj.id = self.bcdb.sqlclient.set(key=None, val=data)
                else:
                    obj.id = self.zdbclient.set(data)
                if self.write_once:
                    obj.readonly = True
                self._logger.debug("NEW:\n%s"%obj)
            else:
                if not self.zdbclient:
                    self.bcdb.sqlclient.set(key=obj.id, val=data)
                else:
                    try:
                        self.zdbclient.set(data, key=obj.id)
                    except Exception as e:
                        if str(e).find("only update authorized")!=-1:
                            raise RuntimeError("cannot update object:%s\n with id:%s, does not exist"%(obj,obj.id))
                        raise e


        if index:
            self.index_set(obj)
            self.index_keys_set(obj)

            if obj.id> self._ids_last:
                bin_id = struct.pack("<I", obj.id)
                j.sal.fs.writeFile(self._ids_file_path, bin_id, append=True)
                self._ids_last = obj.id

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
        with open(self._ids_file_path, "rb") as f:
            while True:
                chunk = f.read(4)
                if chunk:
                    obj_id = struct.unpack("<I", chunk)[0]
                    yield obj_id
                else:
                    break



    def _dict_process_out(self,ddict):
        """
        whenever dict is needed this method will be called before returning
        :param ddict:
        :return:
        """
        return ddict

    def _dict_process_in(self,ddict):
        """
        when data is inserted back into object
        :param ddict:
        :return:
        """
        return ddict


    def new(self,data=None, capnpbin=None):
        if data:
            data = self._dict_process_in(data)
        if data or capnpbin:
            obj = self.schema.get(data=data,capnpbin=capnpbin)
        else:
            obj = self.schema.new()
        obj.model = self
        obj = self._methods_add(obj)
        return obj

    def _methods_add(self,obj):
        return obj

    def _set_pre(self, obj):
        """

        :param obj:
        :return: True,obj when want to store
        """
        for modifier in self._modifiers:
            modifier(self,obj)
        return True,obj

    def index_set(self, obj):
        pass

    def index_keys_set(self,obj):
        pass

    def index_destroy(self):
        pass

    def index_delete(self, obj):
        if not j.data.types.int.check(obj):
            obj = obj.id
        self.index.delete_by_id(obj)

    @queue_method_results
    def get(self, obj_id, return_as_capnp=False,usecache=True,die=True):
        """
        @PARAM id is an int or a key
        @PARAM capnp if true will return data as capnp binary object,
               no hook will be done !
        @RETURN obj    (.index is in obj)
        """


        if obj_id in [None,0,'0',b'0']:
            raise RuntimeError("id cannot be None or 0")

        if self.obj_cache is not None and usecache:
            # print("use cache")
            if obj_id in self.obj_cache:
                epoch,obj = self.obj_cache[obj_id]
                if j.data.time.epoch>self._cache_expiration+epoch:
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
                raise RuntimeError("could not find obj with id:%s"%obj_id)
            else:
                return None


        obj = self.bcdb._unserialize(obj_id, data, return_as_capnp=return_as_capnp,model=self)
        self.obj_cache[obj_id] = (j.data.time.epoch,obj)
        return obj


    def delete_all(self):
        for obj_id in self.id_iterator:
            self._delete2(obj_id)

    def reset(self):
        self._logger.warning("reset:%s"%self.key)
        if self.zdbclient:
            self.delete_all() #only for zdb relevant

        #now need to remove tables from index
        self.index_destroy()

        self.stop()
        j.sal.fs.remove(self._data_dir)

        r = j.clients.credis_core.get("bcdb.instances")
        if r is not None:
            done = False
            r = j.data.serializers.msgpack.loads(r)
            if self.key in r:
                r_id = r.index(self.key)
                r_id2 = "O:%s:*"%r_id
                for key in j.clients.credis_core.keys(r_id2.encode()):
                    j.clients.credis_core.delete(key)
                done = True

            #name needs to stay in the redis because otherwise the index nr will change for the others


        self._init_()

    def iterate(self):
        """
        walk over objects which are of type of this model
        """
        for obj_id in self.id_iterator:
            o=self.get(obj_id)
            yield o


    def get_all(self):
        res = []
        for obj in self.iterate():
            if obj==None:
                raise RuntimeError("iterate should not return None, ever")
            res.append(obj)
        return res

    def _init_index(self):
        pass

    def __str__(self):
        out = "model:%s\n" % self.schema.url
        out += j.core.text.prefix("    ", self.schema.text)
        return out

    __repr__ = __str__
