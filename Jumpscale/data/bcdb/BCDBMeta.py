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
        self._logger_enable()

    def reset(self):
        # make everything in metadata stor empty

        self._reset_runtime_metadata()
        self._bcdb.storclient.delete(0)  # remove the metadata
        self._data = None
        self._load()

    def _reset_runtime_metadata(self):
        # reset the metadata which we can afford to loose
        # all of this can be rebuild from the serialized information of the metastor
        self._data = None
        # self._namespace_last_id = 0
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

        # walk over all schema's let the j.data.schema know that these schema's exist in right order
        for s in self._data.schemas:
            isok = j.data.schema._add_url_to_md5(s.url, s.md5)
            if not isok:
                # means there is a newer one in memory
                schema = j.data.schema.get_from_url_latest(s.url)
                self._schema_set(schema)  # tell our bdcdb metadata that this exists

    def _schemas_in_data_print(self):
        for s in self._data.schemas:
            print(" - %s:%s (%s)" % (s.md5, s.url, s.hasdata))

    def _save(self):
        self._log_debug("save meta:%s" % self._bcdb.name)
        serializeddata = j.data.serializers.jsxdata.dumps(self._data)
        self._bcdb.storclient.set(serializeddata, 0)  # we can now always set at 0 because is for sure already there

    def _schema_set(self, schema):
        """
        add the schema to the metadata if it was not done yet
        :param schema:
        :return: the model id
        """
        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise j.exceptions.Base("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        if not self._schema_exists(schema):
            s_obj = self._data.schemas.new()
            s_obj.url = schema.url
            s_obj.text = schema.text  # + "\n"  # only 1 \n at end
            s_obj.md5 = schema._md5
            s_obj.hasdata = schema.hasdata
            self.schemas_md5.append(schema._md5)
            self._url_mid_set(schema)
            self._save()

    def _url_mid_set(self, schema):
        url = schema.url
        last = 0
        if not url in self._data.url_to_mid:
            # look for the last one
            for item in self._data.url_to_mid.values():
                if int(item) > last:
                    last = int(item)
            self._data.url_to_mid[url] = last + 1

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
