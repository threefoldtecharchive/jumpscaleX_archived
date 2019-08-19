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

# does not use the schema's any more, now custom dict


class BCDBMeta(j.application.JSBaseClass):
    """
    #datamodel

    {
        "url":
            {$url:[mid,[]]}     #latest md5 is at end of list, nid is the model id
        "md5":
            {
                $md5:
                    {
                        "text":$text,
                        "epoch":$epoch,
                        "hasdata":$hasdata
                        "url":$url
                    }
            }
    }

    """

    def init2(self, bcdb=None):
        assert bcdb
        self._logger_enable()
        self._load()

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

    def _load(self):
        self._reset_runtime_metadata()
        serializeddata = self._bcdb.storclient.get(0)
        if serializeddata is None:
            self._log_debug("save, empty schema")
            data = {"url": {}, "md5": {}}
            serializeddata = j.data.serializers.msgpack.dumps(data)
            self._bcdb.storclient.set(serializeddata)
        else:
            self._log_debug("schemas load from db")
            self._data = j.data.serializers.msgpack.loads(serializeddata)

        for d in self.schema_dicts:
            # this will guarantee right order and make sure the j.data.schema knows about the new schemas
            self._add_to_schema_factory(md5=d["md5"], schema_text=d["text"])

    @property
    def schema_dicts(self):
        """
        will walk over the data in the right order (oldest to newest and url's sorted)
        :return:
        """
        urls = [i for i in self._data["url"].keys()]
        urls.sort()
        for url in urls:
            mid, md5s = self._data["url"][url]
            for md5 in md5s:
                d = self._data["md5"][md5]
                yield d

    def _add_to_schema_factory(self, md5, schema_text):
        # don't load the full schema but put the text of schema there
        if not j.data.schema.exists(md5=md5):
            j.data.schema._md5_to_schema[md5] = schema_text

    def _schemas_in_data_print(self):
        print(j.core.tools._data_serializer_safe(self._data))

    def _save(self):
        self._log_debug("save meta:%s" % self._bcdb.name)
        serializeddata = j.data.serializers.msgpack.dumps(self._data)
        self._bcdb.storclient.set(serializeddata, 0)  # we can now always set at 0 because is for sure already there

    def _schema_set(self, schema):
        """
        add the schema to the metadata if it was not done yet
        :param schema:
        :return: the model id
        """

        # optimized for speed, will happen quite a lot, need to know when there is change

        def find_mid():
            mid_highest = 1
            for mid, md5s in self._data["url"].values():
                if mid > mid_highest:
                    mid_highest = mid
            return mid_highest

        if not isinstance(schema, j.data.schema.SCHEMA_CLASS):
            raise j.exceptions.Base("schema needs to be of type: j.data.schema.SCHEMA_CLASS")

        change = False  # we only want to save is there is a change

        # deal with making sure that the md5 of this schema is registered as the newest one
        if schema.url in self._data["url"]:
            mid, md5s = self._data["url"][schema.url]
            if schema._md5 in md5s:
                if schema._md5 != md5s[-1]:
                    # means its not the latest one
                    change = True
                    md5s.pop(md5s.index(schema._md5))
                    md5s.append(schema._md5)  # now at end of list again
                    d = [mid, md5s]
            else:
                # is a new one, not in list yet
                change = True
                d = [mid, [schema._md5]]
        else:
            change = True
            d = [find_mid(), [schema._md5]]
        if change:
            self._data["url"][schema.url] = d

        change2 = False
        if schema._md5 not in self._data["md5"]:
            change2 = True
            d = {}
            d["text"] = schema.text
            d["hasdata"] = schema.hasdata
            d["epoch"] = j.data.time.epoch
            d["url"] = schema.url
            self._data["md5"][schema._md5] = d

        if change or change2:
            self._save()

        # don't load the full schema but put the text of schema there
        self._add_to_schema_factory(md5=schema._md5, schema_text=schema.text)

        # need to check in j.data.schema that this schema is the newest version
        # this is important if someone does j.data.schema.
        j.data.schema._add_md5_to_url(url=schema.url, md5=schema._md5)

    def _data_from_url(self, url):
        if url not in self._data["url"]:
            raise j.exceptions.Input("cannot find url in bcbd:%s" % url)
        if len(self._data["url"][url]) == 0:
            raise j.exceptions.Input("cannot find a schema for url in bcbd:%s (no md5s)" % url)
        md5 = self._data["url"][url][-1]
        if md5 not in self._data["md5"]:
            raise j.exceptions.Input("cannot find md5 in bcbd metadata:%s" % md5)
        return self._data["md5"][md5]

    def _mid_from_url(self, url):
        d = self._data_from_url(url)
        return d["mid"]

    def _schema_exists(self, md5):
        return md5 in self._data["md5"]

    def _schema_delete(self, md5):
        if self._schema_exists(md5):
            self._data["md5"].pop(md5)

    def hasdata_set(self, schema):
        assert schema.hasdata  # needs to be True because thats what we need to set
        if not self._schema_exists(schema._md5):
            raise j.exceptions.Value("did not find schema:%s in metadata" % schema._md5)
        if not self._data["md5"][schema._md5]["hasdata"]:
            # only save when not set yet
            self._data["md5"][schema._md5]["hasdata"] = True
            self._save()

    def __repr__(self):
        return str(self._schemas_in_data_print())

    __str__ = __repr__
