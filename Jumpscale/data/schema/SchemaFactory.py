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
        self.reset()
        self._JSXObjectClass = JSXObject
        self.models_in_use = False  # if this is set then will not allow certain actions to happen here

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
        self._url_to_md5 = {}  # NO LONGER A LIST
        self._md5_to_schema = {}

    def exists(self, md5=None, url=None):
        if md5:
            return md5 in self._md5_to_schema
        elif url:
            return url in self._url_to_md5

    def get_from_md5(self, md5):
        """
        :param md5: each schema has a unique md5 which is its identification string
        :return: Schema
        """
        assert isinstance(md5, str)
        if md5 in self._md5_to_schema:
            schema_text_or_obj = self._md5_to_schema[md5]
            if isinstance(schema_text_or_obj, str):
                if item.strip() == "":
                    raise j.exceptions.JSBUG("schema should never be empty string")
                schema = self._text_to_schema_obj(schema_text_or_obj)
                self._md5_to_schema[md5] = schema
            return self._md5_to_schema[md5]
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
            return self._url_to_md5[url]
        if die:
            raise j.exceptions.Input("Could not find schema with url:%s" % url)

    def get_from_text_multiple(self, schema_text, url=None):
        """
        will return the first schema specified if more than 1

        Returns:
            Schema
        """
        assert isinstance(schema_text, str)
        self._check_bcdb_is_not_used()
        res = []
        blocks = self._schema_blocks_get(schema_text)
        if len(blocks) > 1 and url:
            raise j.exceptions.Input("cannot support add from text with url if more than 1 block")
        for block in blocks:
            res.append(self.get_from_text(block, url=url))
        return res

    def get_from_text(self, schema_text, url=None):
        """
        can only be 1 schema

        Returns:
            Schema
        """
        assert isinstance(schema_text, str)
        md5 = self._add_text_to_schema_obj(schema_text=schema_text, url=url)
        self.get_from_md5(md5)

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

    def _check_bcdb_is_not_used(self):
        if self.models_in_use:
            raise j.exceptions.JSBUG("should not modify schema's when models used through this interface")

    def _add_text_to_schema_obj(self, schema_text, url=None):
        """
        add the text to our structure and conver to schema object
        :param schema_text:
        :param url:
        :return:
        """
        self._check_bcdb_is_not_used()
        md5 = self._md5(schema_text)
        if md5 in self._md5_to_schema:
            return md5

        s = Schema(text=schema_text, md5=md5, url=url)

        self._md5_to_schema[md5] = s

        assert s.url

        return self._md5_to_schema[md5]

    def add_from_path(self, path=None):
        """
        :param path, is path where there are .toml schema's which will be loaded

        will not load model files, only toml !

        """
        self._check_bcdb_is_not_used()
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
