from Jumpscale import j
from .BCDBModel import BCDBModel
from .BCDBMeta import BCDBMeta

JSBASE = j.application.JSBaseClass


class BCDBVFS(j.application.JSBaseClass):
    """
    Virtual File System
    navigate through the BCDB like it was a file system
    the root directory is the bcdb name 
    Here is the file system directories
    / should list all the bcdbs
     /$(bcdb_name)
        /data
            /$(nid)
                /sid
                    /1
                        object1
                        object2
                /hash
                    /0eccf565df45
                        object1
                        object2
                /url
                    /ben.test.1
                        object1
                        object2
        /schemas
            /sid
                1
            /hash
                0eccf565df45
            /url
                ben.test.1 (url / properties of the schema itself)
            /url2sid
                ben.test.1
    info
    eg. test/data/2/url/ben.test.1/object1, test/schemas/hash/0eccf565df45 
    if bcdb name is set eg. /data/2/url/ben.test.1/, data/2/url/ben.test.1/object2,

    On each level we can do 
    - get 
        retrieve a file or a directory given the specified path
    - len
        file length if the current path is a file
        throws if the current path is a directory
    - set
        set a file inside the current path
        throws if the current path is a directory
    - list 
        List the files of a directory
        throws if the current path is a file
    - delete
        delete a file or a directory given the specified path
 

    Attributes:
        _dirs_cache: dictionnary of cached directories.
        serializer: serializer.
        root_dir: BCDB name aka root directory.
        _bcdb: link to bcdb instance
        _first_level_path: all the paths that are right after root
    """

    def __init__(self, bcdb_instances, serialize_format="json"):
        """
        :param bcdb_instances:  all the BCDB instances
        """
        JSBASE.__init__(self)
        self._dirs_cache = {}
        # todo add more serializers
        assert bcdb_instances
        self.serializer = j.data.serializers.json
        self._bcdb_instances = bcdb_instances
        self._bcdb_names = list(bcdb_instances.keys())
        self.current_bcbd_name = self._bcdb_names[0]
        self._bcdb = bcdb_instances[self.current_bcbd_name]
        self.directories_under_data_namespace = ["sid", "hash", "url"]
        self.directories_under_schemas = ["sid", "hash", "url", "url2sid"]
        self.directories_under_root = ["data", "schemas", "info"]

    def change_current_bcdb(self, bcdb_name):
        if bcdb_name in self._bcdb_names and self.current_bcbd_name != bcdb_name:
            self.current_bcbd_name = bcdb_name
            self._bcdb = self._bcdb_instances[bcdb_name]
        else:
            raise RuntimeError("cannot change current bcdb name:%s is not in:%s" % (bcdb_name, self._bcdb_names))

    def _split_clean_path(self, path):
        if path:
            splitted = path.lower().split("/")
            # let's remove all the empty parts
            splitted = list(filter(None, splitted))
            if len(splitted) == 0:  # it means we are at the root directory of the current bcdb
                return []
            else:  # one or more elements
                if (
                    splitted[0] == self.current_bcbd_name
                ):  # if the first element is the current bcdb just remove it and restart
                    splitted.pop(0)
                    if len(splitted) > 0:
                        return self._split_clean_path("/".join(splitted))
                    else:
                        return [self.current_bcbd_name]
                elif splitted[0] in self._bcdb_names:  # we have to set the bcdb to the current one and restart
                    self.change_current_bcdb(splitted[0])
                    splitted.pop(0)
                    if len(splitted) > 0:
                        return self._split_clean_path("/".join(splitted))
                    else:
                        return [self.current_bcbd_name]
                elif splitted[0] in self.directories_under_root:  # it is either data schemas or info
                    return [w.lower() for w in splitted]
                else:
                    raise RuntimeError(
                        "first element:%s of path:%s should be in:%s or an existing bcdb name:%s"
                        % (splitted[0], path, self.directories_under_root, self._bcdb_names)
                    )
        else:
            return []

    def get(self, path):
        splitted = self._split_clean_path(path)
        print("################### path:%s splited:%s" % (path, splitted))
        if len(splitted) > 0:
            key = None
            if splitted[0] == "data":
                key = self._get_data(splitted, path)
            elif splitted[0] == "schemas":
                key = self._get_schemas(splitted, path)
            elif splitted[0] == "info":
                key = "%s_info" % self.current_bcbd_name
                if not key in self._dirs_cache:
                    self._dirs_cache[key] = BCDBVFS_Info(self)
            elif len(splitted) == 1 and splitted[0] == self.current_bcbd_name:
                key = "directories_under_root"
                if not key in self._dirs_cache:
                    self._dirs_cache[key] = BCDBVFS_Data_Dir(self, items=self.directories_under_root)
            else:
                raise RuntimeError("should not happen if _split_clean_path has done properly its job")
        else:
            # it means that we are listing the root directory
            key = "root"
            if not key in self._dirs_cache:
                self._dirs_cache[key] = BCDBVFS_Data_Dir(self, items=self._bcdb_names)
        return self._dirs_cache[key]

    def _get_data_items(self, splitted, nid, path):
        path_length = len(splitted)
        if path_length >= 3 and path_length <= 5:
            if splitted[2] == "sid":
                if path_length == 3:
                    # third element must be the in the list e.g. /data/5/sid
                    key = "%s_data_%s_sid" % (self.current_bcbd_name, nid)
                    if not key in self._dirs_cache:
                        self._dirs_cache[key] = BCDBVFS_Data_Dir(
                            self, items=self._bcdb.meta._schema_md5_to_sid.values()
                        )
                else:
                    try:
                        sid = int(splitted[3])
                    except:
                        raise RuntimeError("sid element:%s of path:%s must be an integer" % (splitted[3], path))
                    if path_length == 4:
                        # fourth element must be the schema identifier e.g. /data/5/sid/5
                        # we should get all the object under the namespace id
                        key = "%s_data_%s_sid_%s" % (self.current_bcbd_name, nid, sid)
                        # if we go through md5 url or sid that will points to the same objects
                        if not key in self._dirs_cache:
                            self._dirs_cache[key] = BCDBVFS_Data_Dir(
                                self, items=self._bcdb.model_get_from_sid(sid).iterate(nid)
                            )
                    else:
                        # fifth element must be the object identifier e.g. /data/5/sid/1/7 or /data/5/url/ben.test.1/7
                        try:
                            id = int(splitted[4])
                        except:
                            raise RuntimeError(
                                "fifth id element:%s of path:%s must be an integer" % (splitted[4], path)
                            )
                        key = "%s_data_%s_sid_%s_%s" % (self.current_bcbd_name, nid, sid, id)
                        if not key in self._dirs_cache:
                            m = self._bcdb.model_get_from_sid(sid)
                            self._dirs_cache[key] = BCDBVFS_Data(self, key=key, model=m, item=m.get(id))
            elif splitted[2] == "hash":
                if path_length == 3:
                    # third element must be the in the list e.g. /data/5/hash
                    key = "%s_data_%s_hash" % (self.current_bcbd_name, nid)
                    if not key in self._dirs_cache:
                        self._dirs_cache[key] = BCDBVFS_Data_Dir(self, items=j.data.schema.url_to_md5.values())
                else:
                    hsh = splitted[3]
                    schema = j.data.schema.get_from_md5(hsh)
                    if path_length == 4:
                        # fourth element must be the schema identifier e.g. /data/5/hash/ec541123d21b
                        # we should get all the object under the namespace id
                        key = "%s_data_%s_hash_%s" % (self.current_bcbd_name, nid, hsh)
                        # if we go through md5 url or sid that will points to the same objects
                        if not key in self._dirs_cache:

                            self._dirs_cache[key] = BCDBVFS_Data_Dir(
                                self, items=self._bcdb.model_get_from_schema(schema).iterate(nid)
                            )
                    else:
                        # fifth element must be the object identifier e.g. /data/5/sid/1/7 or /data/5/url/ben.test.1/7
                        try:
                            id = int(splitted[4])
                        except:
                            raise RuntimeError(
                                "fifth id element:%s of path:%s must be an integer" % (splitted[4], path)
                            )
                        key = "%s_data_%s_hash_%s_%s" % (self.current_bcbd_name, nid, hsh, id)
                        if not key in self._dirs_cache:
                            m = self._bcdb.model_get_from_schema(schema)
                            self._dirs_cache[key] = BCDBVFS_Data(self, key=key, model=m, item=m.get(id))
            else:  # URL
                if path_length == 3:
                    # third element must be the in the list e.g. /data/5/sid
                    key = "%s_data_%s_url" % (self.current_bcbd_name, nid)
                    if not key in self._dirs_cache:
                        self._dirs_cache[key] = BCDBVFS_Data_Dir(self, items=j.data.schema.url_to_md5.keys())
                else:
                    url = splitted[3]
                    if path_length == 4:
                        # fourth element must be the schema identifier e.g. /data/5/url/ben.test.1
                        # we should get all the object under the namespace id
                        key = "%s_data_%s_url_%s" % (self.current_bcbd_name, nid, url)
                        # if we go through md5 url or sid that will points to the same objects
                        if not key in self._dirs_cache:
                            self._dirs_cache[key] = BCDBVFS_Data_Dir(
                                self, items=self._bcdb.model_get_from_url(url).iterate(nid)
                            )
                    else:
                        # fifth element must be the object identifier e.g. /data/5/sid/1/7 or /data/5/url/ben.test.1/7
                        try:
                            id = int(splitted[4])
                        except:
                            raise RuntimeError(
                                "fifth id element:%s of path:%s must be an integer" % (splitted[4], path)
                            )
                        key = "%s_data_%s_url_%s_%s" % (self.current_bcbd_name, nid, url, id)
                        if not key in self._dirs_cache:
                            m = self._bcdb.model_get_from_url(url)
                            self._dirs_cache[key] = BCDBVFS_Data(self, key=key, model=m, item=m.get(id))
        else:
            raise RuntimeError("path:%s too long " % (path))
        return key

    def _get_data(self, splitted, path):
        # check if we are only asking for the data directory
        if len(splitted) == 1:
            key = "%s_data" % self.current_bcbd_name
            if not key in self._dirs_cache:
                self._dirs_cache[key] = BCDBVFS_Data_Dir(self, items=self._bcdb.meta.data.namespaces)
        else:
            try:
                nid = int(splitted[1])
            except:
                raise RuntimeError("Second element:%s of path:%s should be the namespace id" % (splitted[1], path))
            if len(splitted) == 2:
                # second element must be the nid e.g. /data/5
                key = "%s_data_%s" % (self.current_bcbd_name, nid)
                if not key in self._dirs_cache:
                    self._dirs_cache[key] = BCDBVFS_Data_Dir(self, items=self.directories_under_data_namespace)
            else:
                if splitted[2] not in self.directories_under_data_namespace:
                    raise RuntimeError(
                        "third element:%s of path:%s should be in:%s"
                        % (splitted[2], path, self.directories_under_data_namespace)
                    )
                key = self._get_data_items(splitted, nid, path)
        return key

    def _get_schemas(self, splitted, path):
        """find schema(s) corresponding to the path splitted in list elements
        
        Arguments:
            splitted {[list of string]} -- [path splitted in list elements]
        
        Raises:
            RuntimeError: [when elements in path are not correct]
        
        Returns:
            [string] -- [key inserted in the _dirs_cache dictionnary linked to the schema(s) ]
        """
        res = None
        # check if we are only asking for the data directory
        if len(splitted) == 1:
            key = "schemas"
            if not key in self._dirs_cache:
                res = BCDBVFS_Schema_Dir(self, items=self.directories_under_schemas)
        else:
            if splitted[1] not in self.directories_under_schemas:
                raise RuntimeError(
                    "Second element:%s of path:%s should be in:%s" % (splitted[1], path, self.directories_under_schemas)
                )

            if splitted[1] == "sid":
                if len(splitted) == 2:
                    ## directory listing
                    key = "schemas_sid"
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema_Dir(self, items=self._bcdb.meta._schema_md5_to_sid.values())
                else:
                    try:
                        sid = int(splitted[3])
                        key = "schemas_sid_%s" % (sid)
                        if not key in self._dirs_cache:
                            res = BCDBVFS_Schema(
                                self, key=key, schema=self._find_schema_by_id(self._bcdb.data.schema, sid)
                            )
                    except:
                        raise RuntimeError("sid element:%s of path:%s must be an integer" % (splitted[3], path))
            elif splitted[1] == "hash":
                if len(splitted) == 2:
                    ## directory listing
                    key = "schemas_hash"
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema_Dir(self, items=self._bcdb.meta._schema_md5_to_sid.keys())
                else:
                    hsh = splitted[3]
                    key = "schemas_hash_%s" % (hsh)
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema(self, key=key, schema=j.data.schema.get_from_md5(hsh))
            elif splitted[1] == "url":
                if len(splitted) == 2:
                    ## directory listing
                    key = "schemas_url"
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema_Dir(self, items=j.data.schema.url_to_md5.keys())
                else:
                    url = splitted[2]
                    key = "schemas_url_%s" % (url)
                    if not key in self._dirs_cache:
                        s = j.data.schema.get_from_url_latest(url)
                        res = BCDBVFS_Schema(self, key=key, schema=s)
            else:
                raise RuntimeError(
                    "Second element:%s of path:%s should be either sid hash or url" % (splitted[2], path)
                )
        if res is not None:
            self._dirs_cache[key] = res
        return key

    def _find_schema_by_id(self, schemas, sid):
        # TODO OPTIMIZE OR FIND ANOTHER WAY
        for s in schemas:
            if s.sid == sid:
                return s
        return None

    def list(self, path):
        return self.get(path).list()

    def is_dir(self, path):
        self.get(path).is_dir()

    def set(self, path, items=None):
        """set new items on the specified path
        
        Arguments:
            path {string} -- the destination path were the objects will be added
 
        Keyword Arguments:
            items {Schema | JSXObject} -- items to be added in the specified path (default: {None})
        """
        # j.data.schema.add_from_text(schema_text, url)
        pass

        """    def _get_schemas_keys_from_text_url(self, schema_text=None):
        keys = None
        if schema_text:
            txt = j.core.text.strip(schema_text)
            for line in txt.split("\n"):
                strip_line = line.lower().strip()
                if strip_line == "" or strip_line.startswith("#"):
                    continue
                if strip_line.startswith("@url"):
                    url = strip_line.split("=")[1]
                    keys[url] = "schemas_url_%s" % url
        return keys """

    def add_schemas(self, schemas_text=None, bcdb_name=None):
        """set new schemas based on their text to the current bcdb
        Keyword Arguments:
            schemas_text {string} -- can be one or several schema text
        Returns:
             list: all the schemas path added to the cache
        """
        path_added = []
        if bcdb_name:
            self.change_current_bcdb(bcdb_name)

        if schemas_text:
            schemas = j.data.schema.add_from_text(schemas_text)
            if schemas:
                for s in schemas:
                    key = "%s_schemas_url_%s" % (self.current_bcbd_name, s.url)
                    path = "%s/schemas/url/%s" % (self.current_bcbd_name, s.url)
                    path_added.append(path)
                    # we do not check if it exist as anyway it will
                    # replace the latest schema with this url
                    self._dirs_cache[key] = BCDBVFS_Schema(self, key=key, schema=s)
        return path_added

    def delete(self, path):
        return self.get(path).delete()

    def len(self):
        return 1

    def _get_serialized_obj(self, obj):

        if isinstance(obj, j.data.schema._JSXObjectClass):
            # TODO test with other serializers
            if isinstance(self.serializer, type(j.data.serializers.json)):
                return obj._json
            else:
                return self.serializer.dumps(obj._json)
        # for meta we use the json representation otherwise it is not serializable
        elif isinstance(obj, j.data.schema.SCHEMA_CLASS):
            return obj._json
        else:
            # here should be standard types
            if isinstance(obj, str):
                return obj
            else:
                return self.serializer.dumps(obj)

    def _get_serialized_list(self, items):
        for o in items:
            yield self._get_serialized_obj(o)

    def _get_nid_from_data_key(self, key):
        splitted = key.lower().split("_")
        # make sure that the first and last element are not empty and not the bcdb name
        if splitted[0] != "data":
            raise RuntimeError("first element:%s of key:%s must be data" % (splitted[0], key))
        try:
            nid = int(splitted[1])
        except:
            raise RuntimeError("second element:%s of key:%s must be an integer" % (splitted[1], key))
        return nid


class BCDBVFS_Data_Dir:
    def __init__(self, vfs, items=[]):
        self.vfs = vfs
        self.items = items

    def delete(self):
        raise RuntimeError("Data directory can't be deleted")

    def list(self):
        return self.vfs._get_serialized_list(self.items)

    def get(self):
        return self

    def set(self):
        raise RuntimeError("Can't set on a directory")

    def len(self):
        raise RuntimeError("Can't do a len on a directory")

    def is_dir(self):
        return True


class BCDBVFS_Schema_Dir:
    def __init__(self, vfs, items=[], model=None):
        # we need to know if we are looking for a directory or a file
        self.vfs = vfs
        self.items = items

    def delete(self):
        raise RuntimeError("Schema directory can't be deleted")

    def list(self):
        return self.vfs._get_serialized_list(self.items)

    def get(self):
        return self

    def set(self):
        raise RuntimeError("Can't set on a schema directory")

    def len(self):
        raise RuntimeError("Can't do a len on a directory")

    def is_dir(self):
        return True


class BCDBVFS_Schema:
    def __init__(self, vfs, key=None, schema=None):
        self.vfs = vfs
        assert vfs
        self.schema = schema
        # key can be None if it is only to set a new schema
        self.key = key

    def list(self):
        raise RuntimeError("Schema can't be listed")

    def get(self):
        if self.schema:
            return self.vfs._get_serialized_obj(self.schema)
        else:
            raise RuntimeError("Schema is not present")

    def set(self, schema_text):
        raise RuntimeError("Schemas can't be overwritten but you can create a new one check add_schemas()")

    def delete(self):
        raise RuntimeError("Schemas can't be deleted")

    def len(self):
        return len(self.vfs.serializer.dumps(self.schema))

    def is_dir(self):
        return False


class BCDBVFS_Data:
    def __init__(self, vfs, key=None, model=None, item=None):
        self.vfs = vfs
        assert vfs
        assert model
        assert key
        self.key = key
        self.item = item
        self.model = model

    def list(self):
        raise RuntimeError("Data can't be listed")

    def delete(self):
        self.model.delete(self.item)
        self.item = None
        return self.vfs._dirs_cache.pop(self.key, None)

    def get(self):
        if self.item:
            return self.vfs._get_serialized_obj(self.item)
        else:
            raise RuntimeError("Data has been deleted")

    def set(self, item_data, id):
        nid = self.vfs._get_nid_from_data_key(self.key)
        self.item = self.model.set_dynamic(item_data, id=id, nid=nid)
        if self.item is None:
            return False
        else:
            return True

    def len(self):
        return len(self.vfs.serializer.dumps(self.item))

    def is_dir(self):
        return False


class BCDBVFS_Info:
    def __init__(self, vfs):
        self.vfs = vfs

    def delete(self):
        raise RuntimeError("Info can't be deleted")

    def list(self):
        raise RuntimeError("Info is not a directory")

    def set(self):
        raise RuntimeError("Info is read only")

    def len(self):
        raise RuntimeError("Info is not a directory")

    def get(self):
        """
        is fake information but needed to let RDM work
        :return:
        """
        C = """
        # Server
        redis_version:4.0.11
        redis_git_sha1:00000000
        redis_git_dirty:0
        redis_build_id:13f90e3a88f770eb
        redis_mode:standalone
        os:Darwin 17.7.0 x86_64
        arch_bits:64
        multiplexing_api:kqueue
        atomicvar_api:atomic-builtin
        gcc_version:4.2.1
        process_id:93263
        run_id:49afb34b519a889778562b7addb5723c8c45bec4
        tcp_port:6380
        uptime_in_seconds:3600
        uptime_in_days:1
        hz:10
        lru_clock:12104116
        executable:/Users/despiegk/redis-server
        config_file:

        # Clients
        connected_clients:1
        client_longest_output_list:0
        client_biggest_input_buf:0
        blocked_clients:52

        # Memory
        used_memory:11436720
        used_memory_human:10.91M
        used_memory_rss:10289152
        used_memory_rss_human:9.81M
        used_memory_peak:14691808
        used_memory_peak_human:14.01M
        used_memory_peak_perc:77.84%
        used_memory_overhead:2817866
        used_memory_startup:980704
        used_memory_dataset:8618854
        used_memory_dataset_perc:82.43%
        total_system_memory:17179869184
        total_system_memory_human:16.00G
        used_memory_lua:37888
        used_memory_lua_human:37.00K
        maxmemory:100000000
        maxmemory_human:95.37M
        maxmemory_policy:noeviction
        mem_fragmentation_ratio:0.90
        mem_allocator:libc
        active_defrag_running:0
        lazyfree_pending_objects:0

        # Persistence
        loading:0
        rdb_changes_since_last_save:66381
        rdb_bgsave_in_progress:0
        rdb_last_save_time:1538289882
        rdb_last_bgsave_status:ok
        rdb_last_bgsave_time_sec:-1
        rdb_current_bgsave_time_sec:-1
        rdb_last_cow_size:0
        aof_enabled:0
        aof_rewrite_in_progress:0
        aof_rewrite_scheduled:0
        aof_last_rewrite_time_sec:-1
        aof_current_rewrite_time_sec:-1
        aof_last_bgrewrite_status:ok
        aof_last_write_status:ok
        aof_last_cow_size:0

        # Stats
        total_connections_received:627
        total_commands_processed:249830
        instantaneous_ops_per_sec:0
        total_net_input_bytes:22576788
        total_net_output_bytes:19329324
        instantaneous_input_kbps:0.01
        instantaneous_output_kbps:6.20
        rejected_connections:2
        sync_full:0
        sync_partial_ok:0
        sync_partial_err:0
        expired_keys:5
        expired_stale_perc:0.00
        expired_time_cap_reached_count:0
        evicted_keys:0
        keyspace_hits:76302
        keyspace_misses:3061
        pubsub_channels:0
        pubsub_patterns:0
        latest_fork_usec:0
        migrate_cached_sockets:0
        slave_expires_tracked_keys:0
        active_defrag_hits:0
        active_defrag_misses:0
        active_defrag_key_hits:0
        active_defrag_key_misses:0

        # Replication
        role:master
        connected_slaves:0
        master_replid:49bcd83fa843f4e6657440b7035a1c2314766ac4
        master_replid2:0000000000000000000000000000000000000000
        master_repl_offset:0
        second_repl_offset:-1
        repl_backlog_active:0
        repl_backlog_size:1048576
        repl_backlog_first_byte_offset:0
        repl_backlog_histlen:0

        # CPU
        used_cpu_sys:101.39
        used_cpu_user:64.27
        used_cpu_sys_children:0.00
        used_cpu_user_children:0.00

        # Cluster
        cluster_enabled:0

        # Keyspace
        # db0:keys=10000,expires=1,avg_ttl=7801480
        """
        C = j.core.text.strip(C)
        return self.vfs.serializer.dumps(C)

    def is_dir(self):
        return False
