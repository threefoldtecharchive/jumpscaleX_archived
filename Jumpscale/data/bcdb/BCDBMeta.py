from Jumpscale import j

JSBASE = j.application.JSBaseClass


SCHEMA = """

@url = jumpscale.schemas.meta.1
schemas = (LO) !jumpscale.schemas.meta.schema.1
name = "" (S)

@url = jumpscale.schemas.meta.schema.1
url = ""
sid = 0  #schema id  
text = ""
md5 = ""

"""


class BCDBMeta(j.application.JSBaseClass):

    def __init__(self, bcdb):
        JSBASE.__init__(self)
        self.bcdb = bcdb
        self._meta_local_path = j.sal.fs.joinPaths(self.bcdb._data_dir, "meta.db")
        self._schema = j.data.schema.get(SCHEMA)
        self.reset()

    @property
    def data(self):
        if self._data is None:
            if self.bcdb.zdbclient is not None:
                data = self.bcdb.zdbclient.get(0)
            else:
                # no ZDB used, is a file in local filesystem
                if not j.sal.fs.exists(self._meta_local_path):
                    data = None
                else:
                    data = j.sal.fs.readFile(self._meta_local_path, binary=True)
            if data is None:
                self._log_debug("save, empty schema")
                self._data = self._schema.new()
                self._data.name = self.bcdb.name
            else:
                self._log_debug("schemas load from db")
                self._data = self._schema.get(capnpbin=data)

            if self._data.name != self.bcdb.name:
                raise RuntimeError("name given to bcdb does not correspond with name in the metadata stor")

            for s in self._data.schemas:
                self.url2sid[s.url] = s.sid
                self.md5sid[s.md5] = s.sid
                if s.sid > self._schema_last_id:
                    self._schema_last_id = s.sid

        return self._data

    def reset(self):
        self._data = None
        self.sid2schema = {}
        self.sid2model = {}
        self.md5sid = {}
        self.url2sid = {}
        self._schema_last_id = -1
        self.data

    def save(self):
        if self._data is None:
            self.data
        self._log_debug("save:\n%s" % self.data)
        if self.bcdb.zdbclient is not None:
            # if self.bcdb.zdbclient.get(b'\x00\x00\x00\x00') == None:
            if self.bcdb.zdbclient.get(0) == None:
                # self.bcdb.zdbclient.execute_command("SET","", self._data._data)
                self.bcdb.zdbclient.set(self._data._data)
            else:
                self.bcdb.zdbclient.set(self._data._data, 0)
                # self.bcdb.zdbclient.execute_command("SET",b'\x00\x00\x00\x00', self._data._data)
        else:
            j.sal.fs.writeFile(self._meta_local_path, self._data._data)

    def schema_get_from_md5(self, md5, die=True):
        if md5 not in self.md5sid:
            if die:
                raise RuntimeError("did not find url:%s" % self.url)
            return
        return self.schema_get_from_id(self.md5sid[md5])

    def schema_get_from_id(self, schema_id, die=True):
        if schema_id not in self.sid2schema:
            for s in self._data.schemas:
                if s.sid == schema_id:
                    self.sid2schema[schema_id] = j.data.schema.get(s.text)
                    self.sid2schema[schema_id].sid = schema_id
                    return self.sid2schema[schema_id]
            if die:
                raise RuntimeError("schema_id does not exist in db (id:%s)" % schema_id)
        return self.sid2schema[schema_id]

    def schema_get_from_url(self, url, die=True):
        if url not in self.url2sid:
            if die:
                raise RuntimeError("did not find url:%s" % url)
            else:
                return None
        return self.schema_get_from_id(self.url2sid[url], die=die)

    def model_get_from_id(self, schema_id, bcdb=None):
        if schema_id not in self.sid2model:
            if bcdb is None:
                raise RuntimeError("need to specify bcdb when getting model from schema:%s" % schema_id)
            schema = self.schema_get_from_id(schema_id)
            self.sid2model[schema_id] = bcdb.model_get_from_schema(schema=schema)
            self.bcdb.models[schema.url] = self.sid2model[schema_id]
        return self.sid2model[schema_id]

    def model_get_from_url(self, url, bcdb=None):
        if url not in self.url2sid:
            raise RuntimeError("did not find url:%s" % url)
        return self.model_get_from_id(self.url2sid[url], bcdb=bcdb)

    def model_get_from_md5(self, md5, die=True):
        if md5 not in self.md5sid:
            if die:
                raise RuntimeError("did not find url:%s" % url)
            return
        return self.model_get_from_id(self.md5sid[md5])

    def schema_set(self, schema):
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        self._log_debug("schema set in meta:%s" % schema.url)
        schema_existing = self.schema_get_from_url(schema.url, die=False)
        if schema_existing is not None:  # means exists
            if schema_existing._md5 == schema._md5:
                return schema_existing

        # not known yet in namespace in ZDB
        self._schema_last_id += 1

        s = self.data.schemas.new()
        s.url = schema.url
        s.sid = self._schema_last_id
        s.text = schema.text  # + "\n"  # only 1 \n at end
        s.md5 = j.data.hash.md5_string(s.text)
        self._log_info("new schema in meta:\n%s" % self.data)
        self.save()
        self.url2sid[s.url] = s.sid
        schema.sid = s.sid

        return self.schema_get_from_id(s.sid)

    def __repr__(self):
        return str(self._data)

    __str__ = __repr__
