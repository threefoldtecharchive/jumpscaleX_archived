# Copyright (C) July 2018:  TF TECH NV in Belgium see https://www.threefold.tech/
# In case TF TECH NV ceases to exist (e.g. because of bankruptcy)
#   then Incubaid NV also in Belgium will get the Copyright & Authorship for all changes made since July 2018
#   and the license will automatically become Apache v2 for all code related to Jumpscale & DigitalMe
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.
# LICENSE END


from Jumpscale import j

JSBASE = j.application.JSBaseClass


class BCDBMeta(j.application.JSBaseClass):
    def __init__(self, bcdb):
        JSBASE.__init__(self)
        self._bcdb = bcdb

        self._schema = j.data.schema.get_from_url_latest("jumpscale.bcdb.meta.2")
        # self._redis_key_data = "bcdb:%s:meta:data" % bcdb.name
        self._redis_key_lookup_mid2hash = "bcdb:%s:schemas:mid2hash" % bcdb.name
        self._redis_key_lookup_hash2mid = "bcdb:%s:schemas:hash2mid" % bcdb.name
        self._redis_key_lookup_mid2schema = "bcdb:%s:schemas:mid2schema" % bcdb.name
        self._redis_key_lookup_url2mid = "bcdb:%s:schemas:url2mid " % bcdb.name
        self._redis_key_lookup_mid2url = "bcdb:%s:schemas:mid2url" % bcdb.name
        self._redis_key_lookup_nid2meta = "bcdb:%s:schemas:nid2meta" % bcdb.name

        # the next redis is only used for readonly info, data can be lost any time
        if self._bcdb.storclient.type == "RDB":
            self._redis = self._bcdb.storclient._redis
        else:
            self._redis = j.core.db

        self._logger_enable()

    def reset(self):
        # make everything in metadata stor empty

        self._reset_runtime_metadata()
        r = self._redis
        self._bcdb.storclient.delete(0)  # remove the metadata
        r.delete(self._redis_key_lookup_mid2hash)
        r.delete(self._redis_key_lookup_hash2mid)
        r.delete(self._redis_key_lookup_mid2schema)
        r.delete(self._redis_key_lookup_url2mid)
        r.delete(self._redis_key_lookup_mid2url)
        r.delete(self._redis_key_lookup_nid2meta)
        self._data = None
        self._load()

    def _reset_runtime_metadata(self):
        # reset the metadata which we can afford to loose
        # all of this can be rebuild from the serialized information of the metastor
        self._data = None
        self._schema_last_id = 1  # should never be 0
        # self._namespace_last_id = 0
        self._schema_url_to_mid = {}
        self.schemas_md5 = []  # just to know which ones we already know

    def _load(self):

        self._reset_runtime_metadata()

        serializeddata = self._bcdb.storclient.get(0)

        if serializeddata is None:
            self._log_debug("save, empty schema")
            self._data = self._schema.new()
            self._data.name = self._bcdb.name
            # is the initialization of the db, alsways needs to be done first
            serializeddata = j.data.serializers.jsxdata.dumps(self._data)
            self._bcdb.storclient.set(serializeddata)
        else:
            self._log_debug("schemas load from db")
            self._data = self._schema.new(serializeddata=serializeddata)

        # if self._data.name != self._bcdb.name:
        #    raise j.exceptions.Base("name given to bcdb does not correspond with name in the metadata stor")

        check = []

        self._verify()

        for s in self._data.schemas:
            self._log_debug("load in meta:%s" % s.url)
            if s.md5 in check:
                raise j.exceptions.Base("corrupted metadata index, duplicate in schema")
            check.append(s.md5)
            # make sure jumpscale knows about the schema
            schema = j.data.schema._add_from_text_item(s.text, bcdb_check=False)
            schema.hasdata = s.hasdata  # we need to know if there was data in the DB per specific Schema
            self._schema_jsxobj_load(s)
            self._bcdb.model_get_from_schema(schema, schema_set=False)  # IMPORTANT leave schema_set False
            assert self._bcdb._mid_to_model[s.mid].schema._md5  # make sure its not empty
            assert self._bcdb._mid_to_model[s.mid].schema._md5 == s.md5

        # Probably not used anywhere
        # for n in self._data.namespaces:
        #    if n.nid > self._namespace_last_id:
        #        self._namespace_last_id = n.nid
        #    r.hset(self._redis_key_lookup_nid2meta, n._json)

    def _schemas_in_data_print(self):
        for s in self._data.schemas:
            print(" - %s:%s:%s (%s)" % (s.mid, s.md5, s.url, s.hasdata))

    def _verify(self):
        check = []
        for s in self._data.schemas:
            if s.md5 in check:
                raise j.exceptions.Base("corrupted metadata index, duplicate in schema (md5")
            check.append(s.md5)

    def _save(self):
        self._log_debug("save meta:%s" % self._bcdb.name)
        self._verify()
        serializeddata = j.data.serializers.jsxdata.dumps(self._data)
        self._bcdb.storclient.set(serializeddata, 0)  # we can now always set at 0 because is for sure already there

    def _schema_jsxobj_load(self, s):
        """

        :param s: is schema in JSX Object form (so not a Schema object)
        :return:
        """
        r = self._redis

        assert isinstance(s, j.data.schema._JSXObjectClass)

        if s.mid > self._schema_last_id:
            self._schema_last_id = s.mid

        # its only for reference purposes & maybe 3e party usage
        r.hset(self._redis_key_lookup_mid2hash, s.mid, s.md5)
        r.hset(self._redis_key_lookup_hash2mid, s.md5, s.mid)
        r.hset(self._redis_key_lookup_mid2schema, s.mid, s._json)
        r.hset(self._redis_key_lookup_url2mid, s.url, s.mid)
        r.hset(self._redis_key_lookup_mid2url, s.mid, s.url)

        self._schema_url_to_mid[s.url] = s.mid

    def schema_register(self, schema):
        mid = self._schema_set(schema)
        model = self._bcdb._mid_to_model[mid]
        # we need to make sure that the current model uses the newest schema
        model.schema_change(schema)

    def _schema_set(self, schema):
        """
        add the schema to the metadata if it was not done yet
        :param schema:
        :return: the model id
        """
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise j.exceptions.Base("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        # mid is unique per url without version !!!! (THIS IS NEW BEHAVIOR)

        if not self._schema_exists(schema):
            s_obj = self._data.schemas.new()
            s_obj.url = schema.url_noversion

            if schema.url_noversion in self._schema_url_to_mid:
                # means we know the mid not need to do anything
                s_obj.mid = self._schema_url_to_mid
                # self._log_debug("schema was set in BCDB:%s meta:%s (EXISTING)" % (self._bcdb.name, schema.url))
            else:
                s_obj.mid = self._schema_last_id + 0  # make sure copy
                # mid was not known yet so we need to create a new one and remember
                self._schema_url_to_mid[schema.url_noversion] = s_obj.mid
                self._schema_last_id += 1
                self._log_info("new schema in meta:\n%s: %s:%s" % (self._bcdb.name, s_obj.url, s_obj.md5))

            s_obj.text = schema.text  # + "\n"  # only 1 \n at end
            s_obj.md5 = schema._md5
            s_obj.hasdata = schema.hasdata
            self._schema_jsxobj_load(s_obj)
            self._save()
            self.schemas_md5.append(schema._md5)

        return self._schema_url_to_mid[schema.url_noversion]

    def _schema_exists(self, schema):
        return schema._md5 in self.schemas_md5

    def hasdata_set(self, schema):
        assert schema.hasdata  # needs to be True because thats what we need to set
        for s in self._data.schemas:
            # self._log_debug("check hasdata for meta:%s" % s.url)
            if s.md5 == schema._md5:
                if not s.hasdata:
                    s.hasdata = True
                    self._save()
                    return
        raise j.exceptions.Value("did not find schema:%s in metadata" % schema._md5)

    def __repr__(self):
        return str(self._schemas_in_data_print())

    __str__ = __repr__
