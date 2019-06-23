from Jumpscale import j

JSBASE = j.application.JSBaseClass


class BCDBMeta(j.application.JSBaseClass):
    def __init__(self, bcdb, reset=False):
        JSBASE.__init__(self)
        self._bcdb = bcdb

        self._schema = j.data.schema.get_from_url_latest("jumpscale.bcdb.meta.2")
        self._redis_key_data = "bcdb:%s:meta:data" % bcdb.name
        self._redis_key_lookup_sid2hash = "bcdb:%s:schemas:sid2hash" % bcdb.name
        self._redis_key_lookup_hash2sid = "bcdb:%s:schemas:hash2sid" % bcdb.name
        self._redis_key_lookup_sid2schema = "bcdb:%s:schemas:sid2schema" % bcdb.name
        self._redis_key_lookup_url2sid = "bcdb:%s:schemas:url2sid " % bcdb.name
        self._redis_key_lookup_sid2url = "bcdb:%s:schemas:sid2url" % bcdb.name
        self._redis_key_lookup_nid2meta = "bcdb:%s:schemas:nid2meta" % bcdb.name
        self._redis_key_inited = "bcdb:%s:init" % bcdb.name  # if its there it means we have working redis

        if self._bcdb.storclient is None:
            self._log_debug("schemas load from redis")
            r = j.core.db
            # serializeddata = j.core.db.get(self._redis_key_data)
        elif self._bcdb.storclient.type == "RDB":
            self._log_debug("schemas load from redis with RDB")
            r = self._bcdb.storclient._redis
            # serializeddata = r.get(self._redis_key_data)
        else:
            # serializeddata = self._bcdb.storclient.get(0)
            r = j.core.db
        self._redis = r

        self._logger_enable()

        if reset:
            self.reset()
        else:
            self._load()

    def reset(self):
        # make everything in metadata stor empty
        self._reset_runtime_metadata()
        self._data = self._schema.new()
        self._data.name = self._bcdb.name
        r = self._redis
        r.delete(self._redis_key_data)
        self._save()
        self._load()

    def _reset_runtime_metadata(self):
        # reset the metadata which we can afford to loose
        # all of this can be rebuild from the serialized information of the metastor
        self._data = None
        self._schema_last_id = 0
        self._namespace_last_id = 0
        self._sid_to_model = {}
        self._schema_md5_to_sid = {}
        r = self._redis
        r.delete(self._redis_key_lookup_sid2hash)
        r.delete(self._redis_key_lookup_hash2sid)
        r.delete(self._redis_key_lookup_sid2schema)
        r.delete(self._redis_key_lookup_url2sid)
        r.delete(self._redis_key_lookup_sid2url)
        r.delete(self._redis_key_lookup_nid2meta)

    def _load_schema_obj(self, s):
        """

        :param s: is schema in JSX Object form (so not a Schema object)
        :return:
        """
        r = self._redis

        assert isinstance(s, j.data.schema._JSXObjectClass)

        if s.sid > self._schema_last_id:
            self._schema_last_id = s.sid

        if s.sid not in self._sid_to_model:
            # not registered yet, now need to remember in redis and in mem
            self._bcdb.model_get_from_schema(s.text)
            # its only for reference purposes & maybe 3e party usage
            r.hset(self._redis_key_lookup_sid2hash, s.sid, s.md5)
            r.hset(self._redis_key_lookup_hash2sid, s.md5, s.sid)
            r.hset(self._redis_key_lookup_sid2schema, s.sid, s._json)
            r.hset(self._redis_key_lookup_url2sid, s.url, s.sid)
            r.hset(self._redis_key_lookup_sid2url, s.sid, s.url)

        assert self._sid_to_model[s.sid].schema._md5  # make sure its not empty
        assert self._sid_to_model[s.sid].schema._md5 == s.md5
        assert self._schema_md5_to_sid[s.md5]
        assert self._schema_md5_to_sid[s.md5] == s.sid

    def _load(self):

        self._reset_runtime_metadata()

        r = self._redis
        if self._bcdb.storclient is None:
            self._log_debug("schemas load from redis")
            serializeddata = j.core.db.get(self._redis_key_data)
        elif self._bcdb.storclient.type == "RDB":
            self._log_debug("schemas load from redis with RDB")
            serializeddata = r.get(self._redis_key_data)
        else:
            serializeddata = self._bcdb.storclient.get(0)

        if serializeddata is None:
            self._log_debug("save, empty schema")
            self._data = self._schema.new()
            self._data.name = self._bcdb.name
        else:
            self._log_debug("schemas load from db")
            self._data = self._schema.get(serializeddata=serializeddata)

        if self._data.name != self._bcdb.name:
            raise RuntimeError("name given to bcdb does not correspond with name in the metadata stor")

        for s in self._data.schemas:
            self._load_schema_obj(s)

        for n in self._data.namespaces:
            if n.nid > self._namespace_last_id:
                self._namespace_last_id = n.nid

            r.hset(self._redis_key_lookup_nid2meta, n._json)

    def _save(self):

        self._log_debug("save:\n%s" % self)

        serializeddata = j.data.serializers.jsxdata.dumps(self._data)

        if self._bcdb.storclient is None:
            r = j.core.db
            j.core.db.set(self._redis_key_data, serializeddata)
        elif self._bcdb.storclient.type == "RDB":
            r = self._bcdb.storclient._redis
            j.core.db.set(self._redis_key_data, serializeddata)
        else:
            # if self._bcdb.storclient.get(b'\x00\x00\x00\x00') == None:
            if self._bcdb.storclient.get(0) == None:
                # self._bcdb.storclient.execute_command("SET","", self._data._data)
                self._bcdb.storclient.set(serializeddata)
            else:
                self._bcdb.storclient.set(serializeddata, 0)
                # self._bcdb.storclient.execute_command("SET",b'\x00\x00\x00\x00', self._data._data)

    def _schema_set(self, schema):
        """
        add the schema to the metadata if it was not done yet
        :param schema:
        :return:
        """
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        self._log_debug("schema set in BCDB:%s meta:%s (md5:'%s')" % (self._bcdb.name, schema.url, schema._md5))

        # check if the data is already in metadatastor
        if schema._md5 in self._schema_md5_to_sid:
            return self._schema_md5_to_sid[schema._md5]
        else:
            # not known yet in namespace, so is new one
            self._schema_last_id += 1
            s = self._data.schemas.new()
            s.url = schema.url
            s.sid = self._schema_last_id
            s.text = schema.text  # + "\n"  # only 1 \n at end
            s.md5 = schema._md5
            self._load_schema_obj(s)
            self._log_info("new schema in meta:\n%s: %s:%s" % (self, s.url, s.md5))
            self._save()
            return s.sid

    def _schema_exists(self, schema):
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        return schema._md5 in self._bcdb._schema_md5_to_sid

    def __repr__(self):
        return str(self._data)

    __str__ = __repr__
