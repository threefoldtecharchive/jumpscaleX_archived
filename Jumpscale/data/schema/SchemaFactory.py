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


import sys

from .Schema import *
from Jumpscale import j
from .JSXObject import JSXObject

JSBASE = j.application.JSBaseClass


class SchemaFactory(j.application.JSBaseFactoryClass):
    __jslocation__ = "j.data.schema"

    def _init(self, **kwargs):

        self.__code_generation_dir = None
        # self.db = j.clients.redis.core_get()
        self.reset()
        self._JSXObjectClass = JSXObject

    @property
    def SCHEMA_CLASS(self):
        return Schema

    @property
    def _code_generation_dir(self):
        if not self.__code_generation_dir:
            path = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "schema")
            j.sal.fs.createDir(path)
            if path not in sys.path:
                sys.path.append(path)
            j.sal.fs.touch(j.sal.fs.joinPaths(path, "__init__.py"))
            self._log_debug("codegendir:%s" % path)
            self.__code_generation_dir = path
        return self.__code_generation_dir

    def reset(self):
        self._url_to_md5 = {}  # list inside the dict because there can be more than 1 schema linked to url
        self._md5_to_schema = {}

    def exists(self, md5=None, url=None):
        if md5:
            return md5 in self._md5_to_schema
        elif url:
            if not url in self._url_to_md5:
                return False
            return len(self._url_to_md5[url]) > 0
        return False

    def get_from_md5(self, md5):
        """
        :param md5: each schema has a unique md5 which is its identification string
        :return: Schema
        """
        assert isinstance(md5, str)
        md5 = md5.lower()
        if md5 in self._md5_to_schema:
            item = self._md5_to_schema[md5]
            if isinstance(item, str):
                if item.strip() == "":
                    raise j.exceptions.JSBUG("schema should never be empty string")
                return self._add_from_text_item(item)
            return item
        else:
            raise j.exceptions.Input("Could not find schema with md5:%s" % md5)

    def get_from_url(self, url, die=True):
        """
        :param url: url is e.g. jumpscale.bcdb.user.1
        :return: will return the most recent schema, there can be more than 1 schema with same url (changed over time)
        """
        assert isinstance(url, str)
        url = self._urlclean(url)
        if url in self._url_to_md5:
            if len(self._url_to_md5[url]) > 0:
                md5 = self._url_to_md5[url][-1]
                if md5 in self._md5_to_schema:
                    return self.get_from_md5(md5)
                else:
                    if die:
                        raise j.exceptions.Input("Could not find schema with url:%s, schema not loaded yet" % url)
                    else:
                        return md5
        if die:
            raise j.exceptions.Input("Could not find schema with url:%s" % url)

    def get_from_text(self, schema_text, url=None):
        """
        will return the first schema specified if more than 1

        Returns:
            Schema
        """
        assert isinstance(schema_text, str)
        return self.add_from_text(schema_text=schema_text, url=url)[0]

    def _md5(self, text):
        """
        convert text to md5
        """

        original_text = text.replace(" ", "").replace("\n", "").strip()
        # print("*****\n%s\n***********\n"%(ascii_text))
        return j.data.hash.md5_string(original_text)

    def _urlclean(self, url):
        """
        url = j.data.schema._urlclean(url)
        :param url:
        :return:
        """
        return url.strip().strip("'\"").strip()

    def _schema_blocks_get(self, schema_text):
        """
        cut schematext into multiple blocks
        :param schema_text:
        :return:
        """

        block = ""
        blocks = []
        txt = j.core.text.strip(schema_text)
        for line in txt.split("\n"):

            strip_line = line.lower().strip()

            if block == "":
                if strip_line == "" or strip_line.startswith("#"):
                    continue

            if strip_line.startswith("@url"):
                if block is not "":
                    blocks.append(block)
                    block = ""

            block += "%s\n" % line

        # process last block
        if block is not "":
            blocks.append(block)

        return blocks

    def add_from_text(self, schema_text, url=None):
        """
        :param schema_text can be 1 or more schema's in the text
        """
        assert isinstance(schema_text, str)
        res = []
        blocks = self._schema_blocks_get(schema_text)
        if len(blocks) > 1 and url:
            raise j.exceptions.Input("cannot support add from text with url if more than 1 block")
        for block in blocks:
            res.append(self._add_from_text_item(block, url=url))
        return res

    def _add_from_text_item(self, schema_text, url=None):
        md5 = self._md5(schema_text)
        if md5 in self._md5_to_schema:
            r = self._md5_to_schema[md5]
            if not isinstance(r, str):
                # it can be there is already a string there, then we can ignore
                return self._md5_to_schema[md5]

        s = Schema(text=schema_text, md5=md5, url=url)

        self._md5_to_schema[md5] = s

        assert s.url

        isok = self._add_url_to_md5(s.url, s._md5)
        if not isok:
            l = self._url_to_md5[s.url]
            l.pop(l.index(s._md5))
            l.append(s._md5)
            self._url_to_md5[s.url] = l
            # raise j.exceptions.Input("cannot add schema because a newer one already exists", data=schema_text)

        return self._md5_to_schema[md5]

    def _add_url_to_md5(self, url, md5):
        """

        :param url:
        :param md5:
        :return: True if the url & md5 combination is new or latest in row which is ok, otherwise False
        """
        # add md5 to the list if its not there yet
        url = self._urlclean(url)
        if not url in self._url_to_md5:
            self._url_to_md5[url] = []
        if not md5 in self._url_to_md5[url]:
            self._url_to_md5[url].append(md5)
            return True
        if self._url_to_md5[url][-1] == md5:
            return True
        return False

    def add_from_path(self, path=None):
        """
        :param path, is path where there are .toml schema's which will be loaded

        will not load model files, only toml !

        """

        res = []
        # if j.sal.fs
        if j.sal.fs.isFile(path):
            paths = [path]
        else:
            paths = j.sal.fs.listFilesInDir(path, recursive=True, filter="*.toml", followSymlinks=True)
        for schemapath in paths:

            bname = j.sal.fs.getBaseName(schemapath)[:-5]
            if bname.startswith("_"):
                continue

            schema_text = j.sal.fs.readFile(schemapath)
            schemas = j.data.schema.add_from_text(schema_text=schema_text)
            # toml_path = "%s.toml" % (schema.key)
            # if j.sal.fs.getBaseName(schemapath) != toml_path:
            #     toml_path = "%s/%s.toml" % (j.sal.fs.getDirName(schemapath), schema.key)
            #     j.sal.fs.renameFile(schemapath, toml_path)
            for schema in schemas:
                if schema not in res:
                    res.append(schema)
        return res

    def test(self, name=""):
        """
        it's run all tests
        kosmos 'j.data.schema.test()'

        if want run specific test ( write the name of test ) e.g. j.data.schema.test(name="base")
        """
        self._test_run(name=name)
