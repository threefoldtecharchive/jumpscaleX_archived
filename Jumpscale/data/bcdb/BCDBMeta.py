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

        if self._bcdb.zdbclient is None:
            self._log_debug("schemas load from redis")
            r = j.core.db
            data = j.core.db.get(self._redis_key_data)
        elif self._bcdb.zdbclient.type == "RDB":
            self._log_debug("schemas load from redis with RDB")
            r = self._bcdb.zdbclient._redis
            data = r.get(self._redis_key_data)
        else:
            data = self._bcdb.zdbclient.get(0)
            r = j.core.db
        self._redis = r

        if reset:
            self.reset()
        else:
            self._reset()
            self.data

    @property
    def data(self):

        if self._data is None:
            r = self._redis
            if self._bcdb.zdbclient is None:
                self._log_debug("schemas load from redis")
                data = j.core.db.get(self._redis_key_data)
            elif self._bcdb.zdbclient.type == "RDB":
                self._log_debug("schemas load from redis with RDB")
                data = r.get(self._redis_key_data)
            else:
                data = self._bcdb.zdbclient.get(0)

            if data is None:
                self._log_debug("save, empty schema")
                self._data = self._schema.new()
                self._data.name = self._bcdb.name
            else:
                self._log_debug("schemas load from db")
                self._data = self._schema.get(data=data)

            if self._data.name != self._bcdb.name:
                raise RuntimeError("name given to bcdb does not correspond with name in the metadata stor")

            for s in self._data.schemas:
                # find highest schemaid used
                if s.sid > self._schema_last_id:
                    self._schema_last_id = s.sid

                # its only for reference purposes & maybe 3e party usage
                r.hset(self._redis_key_lookup_sid2hash, s.sid, s.md5)
                r.hset(self._redis_key_lookup_hash2sid, s.md5, s.sid)
                r.hset(self._redis_key_lookup_sid2schema, s.sid, s._json)
                r.hset(self._redis_key_lookup_url2sid, s.url, s.sid)
                r.hset(self._redis_key_lookup_sid2url, s.sid, s.url)

                if s.sid in self._bcdb._schema_sid_to_md5:
                    if self._bcdb._schema_sid_to_md5[s.sid] != s.md5:
                        raise RuntimeError("bug: should never happen")
                else:
                    self._bcdb._schema_sid_to_md5[s.sid] = s.md5

                # make sure we know all schema's
                if not j.data.schema.exists(md5=s.md5):
                    j.data.schema.add_from_text(schema_text=s.text)

            for n in self._data.namespaces:
                if n.nid > self._namespace_last_id:
                    self._namespace_last_id = n.nid

                r.hset(self._redis_key_lookup_nid2meta, n._json)

        return self._data

    def reset(self):
        # put new schema
        self._reset()
        self._data = self._schema.new()
        self._data.name = self._bcdb.name
        r = self._redis
        r.delete(self._redis_key_data)
        r.delete(self._redis_key_lookup_sid2hash)
        r.delete(self._redis_key_lookup_hash2sid)
        r.delete(self._redis_key_lookup_sid2schema)
        r.delete(self._redis_key_lookup_url2sid)
        r.delete(self._redis_key_lookup_sid2url)
        r.delete(self._redis_key_lookup_nid2meta)
        self._save()
        self.data

    def _reset(self):
        self._data = None
        self._schema_last_id = 0
        self._namespace_last_id = 0
        self._bcdb._schema_sid_to_md5 = {}
        self._bcdb._schema_md5_to_model = {}

    def _save(self):

        self._log_debug("save:\n%s" % self.data)

        if self._bcdb.zdbclient is None:
            r = j.core.db
            j.core.db.set(self._redis_key_data, self._data._data)
        elif self._bcdb.zdbclient.type == "RDB":
            r = self._bcdb.zdbclient._redis
            j.core.db.set(self._redis_key_data, self._data._data)
        else:
            # if self._bcdb.zdbclient.get(b'\x00\x00\x00\x00') == None:
            if self._bcdb.zdbclient.get(0) == None:
                # self._bcdb.zdbclient.execute_command("SET","", self._data._data)
                self._bcdb.zdbclient.set(self._data._data)
            else:
                self._bcdb.zdbclient.set(self._data._data, 0)
                # self._bcdb.zdbclient.execute_command("SET",b'\x00\x00\x00\x00', self._data._data)

    def _schema_set(self, schema):
        """
        add the schema to the metadata
        :param schema:
        :return:
        """
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        self._log_debug("schema set in BCDB:%s meta:%s" % (self._bcdb.name, schema.url))

        # check if the data is already in metadatastor
        for s in self._data.schemas:
            if s.md5 == schema._md5:
                # found the schema already in stor, return the schema with sid
                schema.sid = s.sid
                return schema

        # not known yet in namespace, so is new one
        self._schema_last_id += 1

        s = self.data.schemas.new()
        s.url = schema.url
        s.sid = self._schema_last_id
        s.text = schema.text  # + "\n"  # only 1 \n at end
        s.md5 = schema._md5
        self._log_debug("new schema in meta:\n%s" % self.data)
        self._save()

        self.reset()  # lets make sure all gets loaded again

        schema.sid = s.sid
        return schema

    def __repr__(self):
        return str(self._data)

    __str__ = __repr__
