from Jumpscale import j


class BCDBVFS:
    """
    Virtual File System
    navigate through the BCDB like it was a file system
    the root directory is the bcdb name 
    Here is the file system directories
    /data
        /nid
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
            ben.test.1
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

    def __init__(self, bcdb_name):
        self._dirs_cache = {}
        self.serializer = j.data.serializers.json
        self.root_dir = bcdb_name
        self._bcdb = j.data.bcdb.get(bcdb_name)
        self.directories_under_data_namespace = ["sid", "hash", "url"]
        self.directories_under_schemas = ["sid", "hash", "url", "url2sid"]
        self.directories_under_root = ["data", "schema", "info"]

    def _split_clean_path(self, path):
        splitted = path.lower().split("/")
        # make sure that the first and last element are not empty and not the bcdb name
        while splitted[0] == "":
            splitted.pop(0)
        while splitted[-1] == "":
            splitted.pop(-1)
        if splitted[0] == self.root_dir:
            splitted.pop(0)
        if splitted[0] not in self._first_level_path:
            raise RuntimeError(
                "first element:%s of path:%s should be in:%s" % (splitted[0], path, self._first_level_path)
            )
        return [w.lower() for w in splitted]

    def get(self, path):
        splitted = self._split_clean_path(path)
        sid = None
        obj_id = None
        hsh = None
        url = None
        key = None
        is_dir = None
        if splitted[0] == "data":
            key = self._get_data(splitted, path)
        elif splitted[0] == "schemas":
            key = self._get_schemas(splitted, path)
        elif splitted[0] == "info":
            key = "info"
            if not key in self._dirs_cache:
                self._dirs_cache[key] = BCDBVFS_Info(self)
        else:
            raise RuntimeError("SHOULD NOT HAPPEN")
        return self._dirs_cache[key]

    def _get_data_items(self, splitted, nid, path):
        path_length = len(splitted) 
        if path_length >= 3 and path_length <= 5:
            if splitted[2] == "sid":
                if path_length == 3:
                # third element must be the in the list e.g. /data/5/sid
                    key = "data_%s_sid" % (nid)
                    if not key in self._dirs_cache:
                        self._dirs_cache[key] = BCDBVFS_Data_Dir(self, splitted,items=self._bcdb._schema_sid_to_md5.keys())
                else:
                    try:
                        sid = int(splitted[3])
                    except:
                        raise RuntimeError("sid element:%s of path:%s must be an integer" % (splitted[3], path))
                    hsh = self._bcdb._schema_sid_to_md5[splitted[3]]
                    if path_length == 4:
                    # fourth element must be the schema identifier e.g. /data/5/sid/5
                    # we should get all the object under the namespace id
                        key = "data_%s_sid_%s" % (nid, sid)
                         # if we go through md5 url or sid that will points to the same objects 
                        if not key in self._dirs_cache:
                            self._dirs_cache[key] = BCDBVFS_Data_Dir(self, splitted,items= bcdb.model_get_from_md5(hsh).iterate(nid))
                    else:
                    # fifth element must be the object identifier e.g. /data/5/sid/1/7 or /data/5/url/ben.test.1/7
                        try:
                            id = int(splitted[4])
                        except:
                            raise RuntimeError("fifth id element:%s of path:%s must be an integer" % (splitted[4], path))
                        key = "data_%s_sid_%s_%s" % (nid, sid, id)
                        if not key in self._dirs_cache:
                            self._dirs_cache[key] = BCDBVFS_Data(self, splitted,item=bcdb.model_get_from_md5(hsh).iterate(nid)(id))
            elif splitted[2] == "hash":
                if path_length == 3:
                # third element must be the in the list e.g. /data/5/hash
                    key = "data_%s_hash" % (nid)
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Data_Dir(self, splitted,items=self._bcdb._schema_sid_to_md5.values())
                else:
                    hsh = splitted[3]
                    if path_length == 4:
                    # fourth element must be the schema identifier e.g. /data/5/hash/ec541123d21b
                    # we should get all the object under the namespace id
                        key = "data_%s_hash_%s" % (nid, hsh)
                         # if we go through md5 url or sid that will points to the same objects 
                        if not key in self._dirs_cache:
                            self._dirs_cache[key] = BCDBVFS_Data_Dir(self, splitted,items= bcdb.model_get_from_md5(hsh).iterate(nid))
                    else:
                    # fifth element must be the object identifier e.g. /data/5/sid/1/7 or /data/5/url/ben.test.1/7
                        try:
                            id = int(splitted[4])
                        except:
                            raise RuntimeError("fifth id element:%s of path:%s must be an integer" % (splitted[4], path))
                        key = "data_%s_hash_%s_%s" % (nid, hsh, id)
                        if not key in self._dirs_cache:
                            self._dirs_cache[key] = BCDBVFS_Data(self, splitted,item=bcdb.model_get_from_md5(hsh).iterate(nid)(id))
            else: #URL
                if path_length == 3:
                # third element must be the in the list e.g. /data/5/sid
                    key = "data_%s_url" % (nid)
                    if not key in self._dirs_cache:
                       self._dirs_cache[key] = BCDBVFS_Data_Dir(self, splitted,items=j.data.schema.url_to_md5.keys())
                else:
                    url = splitted[3]
                    hsh = j.data.schema.url_to_md5[url]
                    if path_length == 4:
                    # fourth element must be the schema identifier e.g. /data/5/url/ben.test.1 
                    # we should get all the object under the namespace id
                        key = "data_%s_url_%s" % (nid, url)
                        # if we go through md5 url or sid that will points to the same objects 
                        if not key in self._dirs_cache:
                            self._dirs_cache[key] = BCDBVFS_Data_Dir(self, splitted,items= bcdb.model_get_from_md5(hsh).iterate(nid))
                    else:
                    # fifth element must be the object identifier e.g. /data/5/sid/1/7 or /data/5/url/ben.test.1/7
                        try:
                            id = int(splitted[4])
                        except:
                            raise RuntimeError("fifth id element:%s of path:%s must be an integer" % (splitted[4], path))
                        key = "data_%s_url_%s_%s" % (nid, url, id)
                        if not key in self._dirs_cache:
                            self._dirs_cache[key] = BCDBVFS_Data(self, splitted,item=(bcdb.model_get_from_md5(hsh).iterate(nid))(id))
        else:
            raise RuntimeError("path:%s too long " % (path))
        return key
            
    def _get_data(self, splitted):
        # check if we are only asking for the data directory
        if len(splitted) == 1:
            key = "data"
            if not key in self._dirs_cache:
                 self._dirs_cache[key] = BCDBVFS_Data_Dir(self, splitted,items=self._bcdb.meta.data.namespaces)
        else:
            try:
                nid = int(splitted[1])
            except:
                raise RuntimeError("Second element:%s of path:%s should be the namespace id" % (splitted[1], path))
            if len(splitted) == 2:
                # second element must be the nid e.g. /data/5
                key = "data_%s" % nid
                if not key in self._dirs_cache: 
                     self._dirs_cache[key] =  BCDBVFS_Data_Dir(self, splitted,items=self.directories_under_data_namespace)
            else:
                if splitted[2] not in self.directories_under_data_namespace:
                    raise RuntimeError("third element:%s of path:%s should be in:%s" % (splitted[2], path, self.directories_under_data_namespace))
                key = self._get_data_items(splitted, nid, path)
        return key
        
    def _get_schemas(self, splitted):
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
                res = BCDBVFS_Schema_Dir(self, splitted, items=self.directories_under_schemas)
        else:
            if splitted[1] not in self.directories_under_schemas:
                    raise RuntimeError("Second element:%s of path:%s should be in:%s" % (splitted[1], path,self.directories_under_schemas))

            if splitted[1] == "sid":
                if len(splitted) == 2:
                    ## directory listing
                    key = "schemas_sid"
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema_Dir(self, splitted, items=self._bcdb._schema_sid_to_md5.keys())
                else: 
                    try:
                        sid = int(splitted[3])
                        key = "schemas_sid_%s" % (sid)
                        if not key in self._dirs_cache:
                            res = BCDBVFS_Schema(self, splitted, schema=self._find_schema_by_id(self._bcdb.data.schema, sid))
                    except:
                        raise RuntimeError("sid element:%s of path:%s must be an integer" % (splitted[3], path))     
            elif splitted[1] == "hash":
                if len(splitted) == 2:
                     ## directory listing
                    key = "schemas_hash"
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema_Dir(self, splitted, items=self._bcdb.data.schema.url_to_md5.values())
                else: 
                    hsh = splitted[3]
                    key = "schemas_hash_%s" % (hsh)
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema(self, splitted, schema=j.data.schema.get_from_md5(hsh))
            elif splitted[1] == "url":
                if len(splitted) == 2:
                    ## directory listing
                    key = "schemas_url"
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema_Dir(self, splitted, items=self._bcdb.data.schema.url_to_md5.keys())
                else: 
                    url = splitted[3]
                    key = "schemas_url_%s" % (url)
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema(self, splitted, schema=j.data.schema.get_from_url_latest(url))
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
        d = self._dir_get(path)
        bname = j.sal.fs.getBasename(path)
        return d.list(bname)
        pass

    def get(self, path):
        # here we should check if we are list the root directory or not
        d = self._dir_get(path)
        bname = j.sal.fs.getBasename(path)
        res = d.get(bname)
        res2 = self.serializer.dumps(res)
        return res2

    def set(self, path):
        pass

    def delete(self, path):
        pass

    def len(self):
        return 1


class BCDBVFS_Data_Dir:
    def __init__(self, vfs,  path_elements,  nid=None):
        self.vfs = vfs
        self.nid = nid
        self.path_elements = path_elements
        self.elements = None

    def list(self):
        if self.elements is None:
            return self.vfs.serializer.dumps(self.elements)
        #could be a list of namespaces / si / hash or urls 
        path_length = len(self.path_elements)
        if path_length == 1:
            # /data directory we should return all the namespaces 
            self.elements = self.vfs._bcdb.meta.data.namespaces
        elif path_length ==2:
            # /data/$nid we should return all the directories_under_data_namespace
            self.elements = self.directories_under_data_namespace
        elif path_length == 3:
            # /data/$nid/sid or /data/$nid/hash or /data/$nid/url
            self.elements = self._get_identifiers_by_type(self.path_elements[2])
        else: 
            # /data/$nid/sid/1/ or /data/$nid/hash/ce4564ed4 or /data/$nid/url/ben.test.1
            self.elements = self._get_objects_from_identifier(self.nid, self.path_elements[2], self.path_elements[3])   
        return self.vfs.serializer.dumps(self.elements)

    def _get_objects_from_identifier(self,nid, identifier_type, id):
        if identifier_type == "sid":
            return self.vfs._bcdb.model_get_from_sid(id).iterate(nid)
        elif identifier_type == "hash":
            return self.vfs._bcdb.model_get_from_md5(id).iterate(nid)
        else: #url
            return self.vfs._bcdb.model_get_from_url(id).iterate(nid)
 


    def get(self):
        pass

    def set(self):
        raise RuntimeError("Can't set on a directory")

    def len(self):
        raise RuntimeError("Can't do a len on a directory")


class BCDBVFS_Schema_Dir:
    def __init__(self, vfs, path_elements, url=None, sid=None, hash=None):
        # we need to know if we are looking for a directory or a file
        assert nid is not None
        self.vfs = vfs
        self.path_elements = path_elements
        self.path_elements = path_elements

    def list(self):
        pass

    def get(self):
        pass

    def set(self):
        pass

    def len(self):
        raise RuntimeError("Can't do a len on a directory")

class BCDBVFS_Data:
    def __init__(self, vfs, is_dir=None, key, nid=None, url=None, sid=None, hash=None):
        # we need to know if we are looking for a directory or a file
        assert is_dir is not None

        self.vfs = vfs
        self.nid = nid
        if url:
            pass
        j.shell()
        self.model

    def list(self):
        pass

    def get(self):
        pass

    def set(self):
        pass

    def len(self):
        pass


class BCDBVFS_Info:
    def __init__(self, vfs):
        self.vfs = vfs

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

