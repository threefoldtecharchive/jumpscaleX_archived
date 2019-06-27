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
                /ben.test.1
                    1


 
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
            raise Exception("cannot change current bcdb name:%s is not in:%s" % (bcdb_name, self._bcdb_names))

    def _split_clean_path(self, path):
        """split the path into elements and returns the element list
        if the path starts with a bcdbname it sets the current bcdb accordingly
        TODO encode the elements so that we can't have characters like underscore 
        that can crash the key generation
        
        Arguments:
            path {[type]} -- [description]
        
        Raises:
            Exception: [description]
        
        Returns:
            [type] -- [description]
        """
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
                    raise Exception(
                        "first element:%s of path:%s should be in:%s or an existing bcdb name:%s"
                        % (splitted[0], path, self.directories_under_root, self._bcdb_names)
                    )
        else:
            return []

        """return the bcdb name or root directory of the path
        if the path begins by data or schemas we will return the 
        current bcdb name
        
        Arguments:
            path {sting} -- path

        Returns:
             string -- bcdb name
        """
        """  def _get_bcdb_name_from_path(self, path):
        splitted = path.lower().split("/")
        # make sure that the first and last element are not empty and not the bcdb name
        while splitted[0] == "":
            splitted.pop(0)
        if splitted[0] == self.root_dir or splitted[0] in self.directories_under_root:
            return self.root_dir
        elif len(splitted) == 1:
            return splitted[0]
        elif  len(splitted) >= 1: """

    def get(self, path):
        splitted = self._split_clean_path(path)
        self._log_info("vfs get path:%s " % path)
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
                key = "directories_under_root"  # to save up some memory space we only use this key
                if not key in self._dirs_cache:
                    self._dirs_cache[key] = BCDBVFS_Data_Dir(self, key, items=self.directories_under_root)
            else:
                raise Exception("should not happen if _split_clean_path has done properly its job")
        else:
            # it means that we are listing the root directory
            key = "root"
            if not key in self._dirs_cache:
                self._dirs_cache[key] = BCDBVFS_Data_Dir(self, key, items=self._bcdb_names)
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
                            self, key, items=self._bcdb.meta._schema_md5_to_sid.values()
                        )
                else:
                    try:
                        sid = int(splitted[3])
                    except:
                        raise Exception("sid element:%s of path:%s must be an integer" % (splitted[3], path))
                    if path_length == 4:
                        # fourth element must be the schema identifier e.g. /data/5/sid/5
                        # we should get all the object under the namespace id
                        key = "%s_data_%s_sid_%s" % (self.current_bcbd_name, nid, sid)
                        # if we go through md5 url or sid that will points to the same objects
                        if not key in self._dirs_cache:
                            m = self._bcdb.model_get_from_sid(sid)
                            self._dirs_cache[key] = BCDBVFS_Data_Dir(self, key, [i for i in m.iterate(nid)], m)
                    else:
                        # fifth element must be the object identifier e.g. /data/5/sid/1/7 or /data/5/url/ben.test.1/7
                        try:
                            id = int(splitted[4])
                        except:
                            raise Exception("fifth id element:%s of path:%s must be an integer" % (splitted[4], path))
                        key = "%s_data_%s_sid_%s_%s" % (self.current_bcbd_name, nid, sid, id)
                        if not key in self._dirs_cache:
                            m = self._bcdb.model_get_from_sid(sid)
                            self._dirs_cache[key] = BCDBVFS_Data(self, key=key, model=m, item=m.get(id))
            elif splitted[2] == "hash":
                if path_length == 3:
                    # third element must be the in the list e.g. /data/5/hash
                    key = "%s_data_%s_hash" % (self.current_bcbd_name, nid)
                    if not key in self._dirs_cache:
                        self._dirs_cache[key] = BCDBVFS_Data_Dir(self, key=key, items=j.data.schema.url_to_md5.values())
                else:
                    hsh = splitted[3]
                    schema = j.data.schema.get_from_md5(hsh)
                    if path_length == 4:
                        # fourth element must be the schema identifier e.g. /data/5/hash/ec541123d21b
                        # we should get all the object under the namespace id
                        key = "%s_data_%s_hash_%s" % (self.current_bcbd_name, nid, hsh)
                        # if we go through md5 url or sid that will points to the same objects
                        if not key in self._dirs_cache:
                            m = self._bcdb.model_get_from_schema(schema)
                            self._dirs_cache[key] = BCDBVFS_Data_Dir(self, key, [i for i in m.iterate(nid)], m)
                    else:
                        # fifth element must be the object identifier e.g. /data/5/sid/1/7 or /data/5/url/ben.test.1/7
                        try:
                            id = int(splitted[4])
                        except:
                            raise Exception("fifth id element:%s of path:%s must be an integer" % (splitted[4], path))
                        key = "%s_data_%s_hash_%s_%s" % (self.current_bcbd_name, nid, hsh, id)
                        if not key in self._dirs_cache:
                            m = self._bcdb.model_get_from_schema(schema)
                            self._dirs_cache[key] = BCDBVFS_Data(self, key=key, model=m, item=m.get(id))
            else:  # URL
                if path_length == 3:
                    # third element must be the in the list e.g. /data/5/sid
                    key = "%s_data_%s_url" % (self.current_bcbd_name, nid)
                    if not key in self._dirs_cache:
                        self._dirs_cache[key] = BCDBVFS_Data_Dir(self, key=key, items=j.data.schema.url_to_md5.keys())
                else:
                    url = splitted[3]
                    if path_length == 4:
                        # fourth element must be the schema identifier e.g. /data/5/url/ben.test.1
                        # we should get all the object under the namespace id
                        key = "%s_data_%s_url_%s" % (self.current_bcbd_name, nid, url)
                        # if we go through md5 url or sid that will points to the same objects
                        if not key in self._dirs_cache:
                            m = self._bcdb.model_get_from_url(url)
                            self._dirs_cache[key] = BCDBVFS_Data_Dir(self, key, [i for i in m.iterate(nid)], m)
                    else:
                        # fifth element must be the object identifier e.g. /data/5/sid/1/7 or /data/5/url/ben.test.1/7
                        try:
                            id = int(splitted[4])
                        except:
                            raise Exception("fifth id element:%s of path:%s must be an integer" % (splitted[4], path))
                        key = "%s_data_%s_url_%s_%s" % (self.current_bcbd_name, nid, url, id)
                        if not key in self._dirs_cache:
                            m = self._bcdb.model_get_from_url(url)
                            self._dirs_cache[key] = BCDBVFS_Data(self, key=key, model=m, item=m.get(id))
        else:
            raise Exception("path:%s too long " % (path))
        return key

    def _get_data(self, splitted, path):
        # check if we are only asking for the data directory
        if len(splitted) == 1:
            key = "%s_data" % self.current_bcbd_name
            if not key in self._dirs_cache:
                # namespaces = self._bcdb.get_all()
                # self._ids_last
                # if len(namespaces) == 0:
                # namespaces = self._bcdb.meta._data.namespaces
                # namespaces = [0]
                self._dirs_cache[key] = BCDBVFS_Data_Dir(self, key=key, items=[1])
        else:
            try:
                nid = int(splitted[1])
            except:
                raise Exception("Second element:%s of path:%s should be the namespace id" % (splitted[1], path))
            if len(splitted) == 2:
                # second element must be the nid e.g. /data/5
                key = "%s_data_%s" % (self.current_bcbd_name, nid)
                if not key in self._dirs_cache:
                    self._dirs_cache[key] = BCDBVFS_Data_Dir(self, key=key, items=self.directories_under_data_namespace)
            else:
                if splitted[2] not in self.directories_under_data_namespace:
                    raise Exception(
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
            Exception: [when elements in path are not correct]
        
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
                raise Exception(
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
                        sid = int(splitted[2])
                        key = "schemas_sid_%s" % (sid)
                        if not key in self._dirs_cache:
                            res = BCDBVFS_Schema(self, key=key, item=self._find_schema_by_id(sid))
                    except:
                        raise Exception("sid element:%s of path:%s must be an integer" % (splitted[2], path))
            elif splitted[1] == "hash":
                if len(splitted) == 2:
                    ## directory listing
                    key = "schemas_hash"
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema_Dir(self, items=self._bcdb.meta._schema_md5_to_sid.keys())
                else:
                    hsh = splitted[2]
                    key = "schemas_hash_%s" % (hsh)
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema(self, key=key, item=self._find_schema_by_hash(hsh))
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
                        res = BCDBVFS_Schema(self, key=key, item=self._find_schema_by_url(url))
            elif splitted[1] == "url2sid":
                if len(splitted) == 2:
                    ## directory listing same as schemas_url
                    key = "schemas_url"
                    if not key in self._dirs_cache:
                        res = BCDBVFS_Schema_Dir(self, items=j.data.schema.url_to_md5.keys())
                else:
                    url = splitted[2]
                    key = "schemas_url2sid_%s" % (url)
                    # should not be cached or should be redone after new schema
                    if not key in self._dirs_cache:
                        s = self._get_url_to_sid_and_hash()
                        res = BCDBVFS_Schema(self, key=key, item=s[url][0])
            else:
                raise Exception("Second element:%s of path:%s should be either sid hash or url" % (splitted[2], path))
        if res is not None:
            self._dirs_cache[key] = res
        return key

    def _get_url_to_sid_and_hash(self):
        md5_to_url = {v[0]: k for k, v in j.data.schema.url_to_md5.items()}
        res = {}
        for k, v in self._bcdb.meta._schema_md5_to_sid.items():
            res[md5_to_url[k]] = (v, k)
        return res

    def _get_hash_to_sid_and_url(self):
        md5_to_url = {v[0]: k for k, v in j.data.schema.url_to_md5.items()}
        res = {}
        for k, v in md5_to_url.items():
            res[k] = (self._bcdb.meta._schema_md5_to_sid[k], v)
        return res

    def _get_sid_to_url_and_hash(self):
        md5_to_url = {v[0]: k for k, v in j.data.schema.url_to_md5.items()}
        res = {}
        for k, v in md5_to_url.items():
            if k in self._bcdb.meta._schema_md5_to_sid:
                res[self._bcdb.meta._schema_md5_to_sid[k]] = (v, k)
        return res

    def _find_schema_by_id(self, sid):
        # TODO OPTIMIZE OR FIND ANOTHER WAY
        for s in self._bcdb.meta._data.schemas:
            if s.sid == sid:
                return s
        return None

    def _find_schema_by_url(self, url):
        # TODO OPTIMIZE OR FIND ANOTHER WAY
        for s in self._bcdb.meta._data.schemas:
            if s.url == url:
                return s
        return j.data.schema.get_from_url_latest(url)

    def _find_schema_by_hash(self, hash):
        # TODO OPTIMIZE OR FIND ANOTHER WAY
        for s in self._bcdb.meta._data.schemas:
            if s.md5 == hash:
                return s
        return j.data.schema.get_from_md5(hash)

    def list(self, path):
        return self.get(path).list()

    def is_dir(self, path):
        self.get(path).is_dir()

    def add_datas(self, data_items, nid, sid, bcdb_name=None):
        """set new data items. To set data we need the bcdb name, namespace id and schema id
        Arguments:
            data_items {list(JSXObject) | JSXObject} -- items to be added in the specified directory 
            bcdb_name {string} -- the bcdb name to be added to if None will use the current one
            nid {integer} -- the namespace to be added to
            sid {integer} -- the schema that the objects follow
        """
        if bcdb_name == None:
            bcdb_name = self.current_bcbd_name
        data_dir = self.get("/%s/data/%s/sid/%s" % (bcdb_name, nid, sid))
        return data_dir.set(data_items)

    def add_schemas(self, schemas_text=None, bcdb_name=None):
        """set new schemas based on their text to the current bcdb
        Keyword Arguments:
            schemas_text {string} -- can be one or several schema text
        Returns:
             list: all the schemas path added to the cache
        """
        added_schemas = []
        if bcdb_name:
            self.change_current_bcdb(bcdb_name)

        if schemas_text:
            schemas = j.data.schema.add_from_text(schemas_text)
            if schemas:
                for s in schemas:
                    self._bcdb.model_get_from_schema(s)
                    r = self._bcdb.meta._schema_set(s)
                    s_obj = self._find_schema_by_id(r)
                    key_url = "%s_schemas_url_%s" % (self.current_bcbd_name, s_obj.url)
                    key_sid = "%s_schemas_sid_%s" % (self.current_bcbd_name, s_obj.sid)
                    key_hash = "%s_schemas_hash_%s" % (self.current_bcbd_name, s_obj.md5) 
                    added_schemas.append(s_obj)
                    # we do not check if it exist as anyway it will
                    # replace the latest schema with this url
                    self._dirs_cache[key_url] = BCDBVFS_Schema(self, key=key_url, item=s_obj)
                    self._dirs_cache[key_sid] = BCDBVFS_Schema(self, key=key_sid, item=s_obj)
                    self._dirs_cache[key_hash] = BCDBVFS_Schema(self, key=key_hash, item=s_obj)
        return added_schemas

    def delete(self, path):
        if self._split_clean_path(path) == []:
            # will change the current bcdb if it has to
            # it means we are trying to remove everything on the current bcdb
            self._log_info("WARNING bcdb:%s reset" % self.current_bcbd_name)
            self._bcdb.reset()
            for o in self._dirs_cache.keys():
                try:
                    self._log_info("deleting:%s" % o)
                    self._dirs_cache[o].delete()
                except:
                    pass
            self._dirs_cache = {}
        else:
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
        # make sure that the second element are not empty
        if splitted[1] != "data":
            raise Exception("first element:%s of key:%s must be data" % (splitted[1], key))
        try:
            nid = int(splitted[2])
        except:
            raise Exception("second element:%s of key:%s must be an integer" % (splitted[2], key))
        return nid

    def _extract_info_from_key(self, key, info_dict=None):
        splitted = key.lower().split("_")
        # let's remove all the empty parts
        splitted = list(filter(None, splitted))
        if info_dict == None:
            info_dict = {}
        # make sure that the first element is iether a bcdb name or in data schemas or info
        if splitted[0] in self.directories_under_root:
            if not "bcdb_name" in info_dict:
                info_dict["bcdb_name"] = self.current_bcbd_name
            info_dict["type"] = splitted[0]
            if splitted[0] == self.directories_under_root[0]:  # data url
                if len(splitted) > 1:  # if true then it is a data nid
                    info_dict["nid"] = splitted[1]
                    if len(splitted) > 2:  # if true then it is a data identifier
                        if not splitted[2] in self.directories_under_data_namespace:
                            raise Exception(
                                "key element:%s must be in:%s" % (splitted[2], self.directories_under_data_namespace)
                            )
                        info_dict["identifier_type"] = splitted[2]
                        if len(splitted) > 3:  # if true then it is a data sid hash or url
                            info_dict["identifier"] = splitted[3]
                            if len(splitted) > 4:  # if true then it is a data id
                                info_dict["obj_id"] = splitted[4]
            else:
                if len(splitted) > 1:  # if true then it is a schemas url
                    info_dict["identifier_type"] = splitted[1]
                    if len(splitted) > 2:  # if true then it is a schema id
                        info_dict["identifier"] = splitted[2]
        else:
            if splitted[0] in self._bcdb_names:
                info_dict["bcdb_name"] = splitted[0]
                key_minus_bcdbname = "_".join(splitted[1:])
                return self._extract_info_from_key(key_minus_bcdbname, info_dict)
            else:
                info_dict["type"] = splitted[0]
        return info_dict

    def _get_model_based_on_info(self, info):
        if info["identifier_type"] == "sid":
            return self._bcdb.model_get_from_sid(info["identifier"])
        elif info["identifier_type"] == "url":
            return self._bcdb.model_get_from_url(info["identifier"])
        elif info["identifier_type"] == "hash":
            schema = j.data.schema.get_from_md5(info["identifier"])
            return self._bcdb.model_get_from_schema(schema)
        else:
            raise Exception("impossible to model from info:%s" % info)

    def _update_cache_for_object_keys(self, keys, obj):
        """update the cache for the provided keys. The item will be replaced if the 
        BCDB_data objet already exist.
        the containing directory will be removed from cache
        
        Arguments:
            keys {tuple(string,string)} -- object_key and the containing directory key
            obj {JSXObj} -- [description]
        """
        for key, dir_key in keys:
            self._log_info("data cache updated key:%s " % (key))
            self._dirs_cache.pop(dir_key, None)
            if not key in self._dirs_cache:
                self._dirs_cache[key] = BCDBVFS_Data(self, key=key, item=obj)
            else:
                self._dirs_cache[key].item = obj

    def _insert_obj(self, model, obj_data, nid, obj_id=None):
        if obj_id:  # it means we are going to update the object
            obj = model.set_dynamic(obj_data, obj_id=int(obj_id), nid=int(nid))
        else:  # it means we are going to create an object
            obj = model.set_dynamic(obj_data, nid=int(nid))
        return obj

    def _insert_data_and_update_cache(self, key, obj_data, model):
        """will change or add the data objects item based on its key 
        and then update the cache for all the possible keys. For instance let's take a 
        schema with id=5 md5=ecf2345 url=test.1 if the current bcdb name is test, the provided key is
        data_1_url_test.1_18. We will update the object and the cache for the keys 
        test_data_1_url_test.1_18, test_data_1_hash_ecf2345_18 and test_data_1_sid_5_18 
        if there is no id at the end of the key we will create a new object

        Arguments:
            key {[type]} -- [description]
            obj_item {[type]} -- [description]
        Returns:
            obj {JSX_Obj} -- the added or inserted obj
        """
        info = self._extract_info_from_key(key)
        if info["type"] == self.directories_under_root[0]:  # must be a data key
            keybase = "%s_data_%s_" % (info["bcdb_name"], info["nid"])
            obj_id = None
            if "obj_id" in info:  # it means we are going to update an object
                obj_id = info["obj_id"]
            obj = self._insert_obj(model, obj_data, info["nid"], obj_id)

            if info["identifier_type"] == self.directories_under_data_namespace[0]:  # sid
                keybase_with_sid = "%ssid_%s" % (keybase, info["identifier"])
                key_with_sid = "%s_%s" % (keybase_with_sid, obj.id)
                # get hash and url corresponding to that id
                conv = self._get_sid_to_url_and_hash()
                url_for_sid = conv[int(info["identifier"])][0]
                keybase_with_url = "%surl_%s" % (keybase, url_for_sid)
                key_with_url = "%s_%s" % (keybase_with_url, obj.id)
                hash_for_sid = conv[int(info["identifier"])][1]
                keybase_with_hash = "%shash_%s" % (keybase, hash_for_sid)
                key_with_hash = "%s_%s" % (keybase_with_hash, obj.id)
            elif info["identifier_type"] == self.directories_under_data_namespace[1]:  # hash
                keybase_with_hash = "%shash_%s" % (keybase, info["identifier"])
                key_with_hash = "%s_%s" % (keybase_with_hash, obj.id)
                # get sid and url corresponding to that id
                conv = self._get_hash_to_sid_and_url()
                sid_for_hash = conv[info["identifier"]][0]
                keybase_with_sid = "%ssid_%s" % (keybase, sid_for_hash)
                key_with_sid = "%s_%s" % (sid_for_hash, obj.id)
                url_for_hash = conv[info["identifier"]][1]
                keybase_with_url = "%surl_%s" % (keybase, url_for_hash)
                key_with_url = "%s_%s" % (keybase_with_url, obj.id)
            elif info["identifier_type"] == self.directories_under_data_namespace[2]:  # url
                keybase_with_url = "%surl_%s" % (keybase, info["identifier"])
                key_with_url = "%s_%s" % (keybase_with_url, obj.id)
                # get hash and sid corresponding to that id
                conv = self._get_url_to_sid_and_hash()
                sid_for_url = conv[info["identifier"]][0]
                keybase_with_sid = "%ssid_%s" % (keybase, sid_for_url)
                key_with_sid = "%s_%s" % (keybase_with_sid, obj.id)
                hash_for_url = conv[info["identifier"]][1]
                keybase_with_hash = "%shash_%s" % (keybase, hash_for_url)
                key_with_hash = "%s_%s" % (keybase_with_hash, obj.id)
            self._update_cache_for_object_keys(
                [
                    (key_with_sid, keybase_with_sid),
                    (key_with_url, keybase_with_url),
                    (key_with_hash, keybase_with_hash),
                ],
                obj,
            )
            return obj
        else:
            raise Exception("key:%s is not a data key. Update cache data can only work with data keys" % key)


class BCDBVFS_Data_Dir:
    def __init__(self, vfs, key, items=[], model=None):
        self.vfs = vfs
        self.items = items
        self._model = model
        self.key = key

    def delete(self):
        info = self.vfs._extract_info_from_key(self.key)
        if "identifier_type" in info:  # make sure that the directory contains data
            for i in self.items:
                self.vfs.get("%s_%s" % (self.key, i.id)).delete()
        else:
            raise Exception("that data directory can't be deleted")

    def _get_model(self):
        if self._model == None:
            info = self.vfs._extract_info_from_key(self.key)
            if "identifier_type" in info:
                self._model = self.vfs._get_model_based_on_info(info)

        return self._model

    def list(self):
        return self.vfs._get_serialized_list(self.items)

    def get(self):
        return self

    def set(self, items_data):
        """set one or multiple item on the directory
        returns the updated or added items
        Arguments:
            items_data {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        if self._get_model():  # make sure that the directory can receive data
            res = []
            if isinstance(items_data, list):
                for data in items_data:
                    res.append(self.vfs._insert_data_and_update_cache(self.key, data, self._model))
            else:
                res.append(self.vfs._insert_data_and_update_cache(self.key, items_data, self._model))
            self.items = [i for i in self._model.iterate(self.vfs._get_nid_from_data_key(self.key))]
            return res
        else:  # we are probably trying to add a doc in a root or bcdb path
            raise Exception("Can't add data to that directory")

    def len(self):
        raise Exception("Can't do a len on a directory")

    def is_read_only(self):
        if self._get_model():
            # if we have a model it means that we can add data item
            return False
        return True

    def is_dir(self):
        return True


class BCDBVFS_Schema_Dir:
    def __init__(self, vfs, items=[], model=None):
        # we need to know if we are looking for a directory or a file
        self.vfs = vfs
        self.items = items

    def delete(self):
        raise Exception("Schema directory can't be deleted")

    def list(self):
        return self.vfs._get_serialized_list(self.items)

    def get(self):
        return self

    def set(self):
        raise Exception("Can't set on a schema directory")

    def len(self):
        raise Exception("Can't do a len on a directory")

    def is_read_only(self):
        return True

    def is_dir(self):
        return True


class BCDBVFS_Schema:
    def __init__(self, vfs, key=None, item=None):
        self.vfs = vfs
        assert vfs
        self.item = item
        # key can be None if it is only to set a new schema
        self.key = key

    def list(self):
        raise Exception("Schema can't be listed")

    def get(self):
        if self.item:
            return self.vfs._get_serialized_obj(self.item)
        else:
            raise Exception("Schema is not present for key:%s" % self.key)

    def new(self, schema_text):
        return self.vfs.add_schemas(schema_text)

    def set(self, schema_text):
        raise Exception("Schemas can't be overwritten but you can create a new one via add_schemas()")

    def is_read_only(self):
        return True

    def delete(self):
        raise Exception("Schemas can't be deleted")

    def len(self):
        return len(self.vfs.serializer.dumps(self.item))

    def is_dir(self):
        return False


class BCDBVFS_Data:
    def __init__(self, vfs, key=None, model=None, item=None):
        self.vfs = vfs
        assert vfs
        assert key
        self.key = key
        self.item = item
        self._model = model

    def list(self):
        raise Exception("Data can't be listed")

    def _get_model(self):
        if self._model == None:
            info = self.vfs._extract_info_from_key(self.key)
            self._model = self.vfs._get_model_based_on_info(info)
        return self._model

    def delete(self):
        self._get_model().delete(self.item)  # removing from db
        self.item = None  # removing from obj memory
        removed_obj = self.vfs._dirs_cache.pop(self.key, None)  # removing from cache
        return removed_obj

    def get(self):
        if self.item:
            return self.vfs._get_serialized_obj(self.item)
        else:
            raise Exception("Data has been deleted")

    def new(self, item_data):
        return self.vfs._insert_data_and_update_cache(self.key, item_data, self._get_model())

    def set(self, item_data):
        """replace the item with the new data
            if item_data contains an id it will not be taken into account
        Arguments:
            item_data {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        return self.vfs._insert_data_and_update_cache(self.key, item_data, self._get_model())

    def len(self):
        return len(self.vfs.serializer.dumps(self.item))

    def is_read_only(self):
        return False

    def is_dir(self):
        return False


class BCDBVFS_Info:
    def __init__(self, vfs):
        self.vfs = vfs

    def delete(self):
        raise Exception("Info can't be deleted")

    def list(self):
        raise Exception("Info is not a directory")

    def set(self):
        raise Exception("Info is read only")

    def len(self):
        raise Exception("Info is not a directory")

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

    def is_read_only(self):
        return True

    def is_dir(self):
        return False
