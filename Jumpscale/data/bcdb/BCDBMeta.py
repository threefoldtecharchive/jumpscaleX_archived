from Jumpscale import j

JSBASE = j.application.JSBaseClass


class BCDBMeta(j.application.JSBaseClass):
    def __init__(self, bcdb):
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
        elif self._bcdb.storclient.type == "RDB":
            self._log_debug("schemas load from redis with RDB")
            r = self._bcdb.storclient._redis
        else:
            r = j.core.db
        self._redis = r

        self._logger_enable()

    def reset(self):
        # make everything in metadata stor empty
        self._reset_runtime_metadata()
        r = self._redis
        r.delete(self._redis_key_data)
        r.delete(self._redis_key_lookup_sid2hash)
        r.delete(self._redis_key_lookup_hash2sid)
        r.delete(self._redis_key_lookup_sid2schema)
        r.delete(self._redis_key_lookup_url2sid)
        r.delete(self._redis_key_lookup_sid2url)
        r.delete(self._redis_key_lookup_nid2meta)
        self._save()
        self._load()

    def _reset_runtime_metadata(self):
        # reset the metadata which we can afford to loose
        # all of this can be rebuild from the serialized information of the metastor
        self._data = None
        self._schema_last_id = 0
        self._namespace_last_id = 0
        self._schema_md5_to_sid = {}
        r = self._redis

    def _data_in_db(self):
        r = self._redis
        if self._bcdb.storclient is None:
            self._log_debug("schemas load from redis")
            serializeddata = j.core.db.get(self._redis_key_data)
        elif self._bcdb.storclient.type == "RDB":
            self._log_debug("schemas load from redis with RDB")
            serializeddata = r.get(self._redis_key_data)
        else:
            serializeddata = self._bcdb.storclient.get(0)
        return serializeddata

    def _load(self):

        self._reset_runtime_metadata()

        serializeddata = self._data_in_db()

        if serializeddata is None:
            self._log_debug("save, empty schema")
            self._data = self._schema.new()
            self._data.name = self._bcdb.name
        else:
            self._log_debug("schemas load from db")
            self._data = self._schema.new(serializeddata=serializeddata)

        if self._data.name != self._bcdb.name:
            raise RuntimeError("name given to bcdb does not correspond with name in the metadata stor")

        for s in self._data.schemas:
            self._log_debug("load in meta:%s" % s.url)
            schema = j.data.schema.get_from_text(s.text)  # make sure jumpscale knows about the schema
            self._schema_jsxobj_load(s)
            self._bcdb.model_get_from_schema(schema, schema_set=True)

            assert self._bcdb._sid_to_model[s.sid].schema._md5  # make sure its not empty
            assert self._bcdb._sid_to_model[s.sid].schema._md5 == s.md5

        # Probably not used anywhere
        # for n in self._data.namespaces:
        #    if n.nid > self._namespace_last_id:
        #        self._namespace_last_id = n.nid
        #    r.hset(self._redis_key_lookup_nid2meta, n._json)

    def _schemas_in_data_print(self):
        for s in self._data.schemas:
            print("%s:%s:%s" % (s.sid, s.md5, s.url))

    def _save(self):

        self._log_debug("save meta:%s" % self._bcdb.name)

        if not self._data:
            self._data = self._schema.new()
            self._data.name = self._bcdb.name
        serializeddata = j.data.serializers.jsxdata.dumps(self._data)

        if self._bcdb.storclient is None:
            r = j.core.db
            j.core.db.set(self._redis_key_data, serializeddata)
        elif self._bcdb.storclient.type == "RDB":
            r = self._bcdb.storclient._redis
            j.core.db.set(self._redis_key_data, serializeddata)
        else:
            if self._bcdb.storclient.get(0) == None:
                self._bcdb.storclient.set(serializeddata)
            else:
                self._bcdb.storclient.set(serializeddata, 0)

    def _schema_jsxobj_load(self, s):
        """

        :param s: is schema in JSX Object form (so not a Schema object)
        :return:
        """
        r = self._redis

        assert isinstance(s, j.data.schema._JSXObjectClass)

        if s.sid > self._schema_last_id:
            self._schema_last_id = s.sid

        # its only for reference purposes & maybe 3e party usage
        r.hset(self._redis_key_lookup_sid2hash, s.sid, s.md5)
        r.hset(self._redis_key_lookup_hash2sid, s.md5, s.sid)
        r.hset(self._redis_key_lookup_sid2schema, s.sid, s._json)
        r.hset(self._redis_key_lookup_url2sid, s.url, s.sid)
        r.hset(self._redis_key_lookup_sid2url, s.sid, s.url)

        self._schema_md5_to_sid[s.md5] = s.sid

    def _schema_set(self, schema):
        """
        add the schema to the metadata if it was not done yet
        :param schema:
        :return:
        """
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        # check if the data is already in metadatastor
        if schema._md5 in self._schema_md5_to_sid:
            self._log_debug("schema set in BCDB:%s meta:%s (EXISTING)" % (self._bcdb.name, schema.url))
            return self._schema_md5_to_sid[schema._md5]
        else:
            self._log_debug("schema set in BCDB:%s meta:%s (md5:'%s')" % (self._bcdb.name, schema.url, schema._md5))
            # not known yet in namespace, so is new one
            self._schema_last_id += 1
            s = self._data.schemas.new()
            s.url = schema.url
            s.sid = self._schema_last_id
            s.text = schema.text  # + "\n"  # only 1 \n at end
            s.md5 = schema._md5
            self._schema_jsxobj_load(s)
            self._log_info("new schema in meta:\n%s: %s:%s" % (self._bcdb.name, s.url, s.md5))
            self._save()
            return s.sid

    def _schema_exists(self, schema):
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        return schema._md5 in self._schema_md5_to_sid

    def __repr__(self):
        return str(self._schemas_in_data_print())

    __str__ = __repr__
