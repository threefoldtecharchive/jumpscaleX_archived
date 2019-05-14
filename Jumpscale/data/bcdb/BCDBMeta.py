from Jumpscale import j

JSBASE = j.application.JSBaseClass



class BCDBMeta(j.application.JSBaseClass):
    def __init__(self, bcdb):
        JSBASE.__init__(self)
        self._bcdb = bcdb
        self._meta_local_path = j.sal.fs.joinPaths(self._bcdb._data_dir, "meta.db")
        self._schema = j.data.schema.get_from_url_latest("jumpscale.schemas.meta.1")
        self.reset()

    @property
    def data(self):
        if self._data is None:
            if self._bcdb.zdbclient is not None:
                data = self._bcdb.zdbclient.get(0)
            else:
                # no ZDB used, is a file in local filesystem
                if not j.sal.fs.exists(self._meta_local_path):
                    data = None
                else:
                    data = j.sal.fs.readFile(self._meta_local_path, binary=True)
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
                #find highest schemaid used
                if s.sid > self._schema_last_id:
                    self._schema_last_id = s.sid

                if s.sid in self._bcdb._schema_sid_to_md5:
                    if self._bcdb._schema_sid_to_md5[s.sid] != s.md5:
                        raise RuntimeError("bug: should never happen")
                else:
                    self._bcdb._schema_sid_to_md5[s.sid] = s.md5

                #make sure we know all schema's
                if not j.data.schema.exists(md5=s.md5):
                    j.data.schema.add_from_text(schema_text=s.text)

        return self._data

    def reset(self):
        self._data = None
        self._schema_last_id = 0
        self.data

    def _save(self):
        if self._data is None:
            self.data
        self._log_debug("save:\n%s" % self.data)
        if self._bcdb.zdbclient is not None:
            # if self._bcdb.zdbclient.get(b'\x00\x00\x00\x00') == None:
            if self._bcdb.zdbclient.get(0) == None:
                # self._bcdb.zdbclient.execute_command("SET","", self._data._data)
                self._bcdb.zdbclient.set(self._data._data)
            else:
                self._bcdb.zdbclient.set(self._data._data, 0)
                # self._bcdb.zdbclient.execute_command("SET",b'\x00\x00\x00\x00', self._data._data)
        else:
            j.sal.fs.writeFile(self._meta_local_path, self._data._data)

    def _schema_set(self, schema):
        """
        add the schema to the metadata
        :param schema:
        :return:
        """
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise RuntimeError("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        self._log_debug("schema set in meta:%s" % schema.url)

        #check if the data is already in metadatastor
        for s in self._data.schemas:
            if s.md5 == schema._md5:
                #found the schema already in stor, return the schema with sid
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

        self.reset() #lets make sure all gets loaded again

        schema.sid = s.sid
        return schema

    def __repr__(self):
        return str(self._data)

    __str__ = __repr__
