import sys

from .Schema import *
from Jumpscale import j
from .DataObjBase import DataObjBase

JSBASE = j.application.JSBaseClass


class SchemaFactory(j.application.JSBaseClass):
    __jslocation__ = "j.data.schema"

    def _init(self):

        self.__code_generation_dir = None
        # self.db = j.clients.redis.core_get()
        self.reset()
        self.DataObjBase = DataObjBase

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
        self.url_to_md5 = {}  # list inside the dict because there can be more than 1 schema linked to url
        self.url_versionless_to_md5 = {}  # list inside the dict because there can be more than 1 schema linked to url
        self.md5_to_schema = {}

    def exists(self, md5=None, url=None):
        if md5:
            return md5 in self.md5_to_schema
        elif url:
            if not url in self.url_to_md5:
                return False
            return len(self.url_to_md5[url]) > 0
        return False

    def get_from_md5(self, md5):
        """
        :param md5: each schema has a unique md5 which is its identification string
        :return: Schema
        """
        assert isinstance(md5, str)
        md5 = md5.lower()
        if md5 in self.md5_to_schema:
            return self.md5_to_schema[md5]
        else:
            raise j.exceptions.Input("Could not find schema with md5:%s" % md5)

    def get_from_url_latest(self, url):
        """
        :param url: url is e.g. jumpscale.bcdb.user.1
        :return: will return the most recent schema, there can be more than 1 schema with same url (changed over time)
        """
        assert isinstance(url, str)
        url = self._urlclean(url)
        if url in self.url_to_md5:
            if len(self.url_to_md5[url]) > 0:
                md5 = self.url_to_md5[url][-1]
                return self.md5_to_schema[md5]
        raise j.exceptions.Input("Could not find schema with url:%s" % url)

    def get_from_text(self, schema_text, url=None):
        """
        will return the first schema specified if more than 1

        Returns:
            Schema
        """
        assert isinstance(schema_text, str)
        if schema_text != "":
            if j.data.types.string.check(schema_text):
                schema = self.add_from_text(schema_text=schema_text, url=url)[0]
            else:
                raise j.exceptions.Input("Schema needs to be text ")

        return schema

    def _md5(self, text):
        """
        convert text to md5
        """

        original_text = text.replace(" ", "").replace("\n", "").strip()
        # print("*****\n%s\n***********\n"%(ascii_text))
        return j.data.hash.md5_string(original_text)

    def _urlclean(self, url):
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
        if md5 in self.md5_to_schema:
            return self.md5_to_schema[md5]

        s = Schema(text=schema_text, md5=md5, url=url)

        # add md5 to the list if its not there yet
        if not s.url in self.url_to_md5:
            self.url_to_md5[s.url] = []
        if not s._md5 in self.url_to_md5[s.url]:
            self.url_to_md5[s.url].append(s._md5)

        # add md5 to the list if its not there yet for versionless
        if not s.url_noversion in self.url_versionless_to_md5:
            self.url_versionless_to_md5[s.url_noversion] = []
        if not s._md5 in self.url_versionless_to_md5[s.url_noversion]:
            self.url_versionless_to_md5[s.url_noversion].append(s._md5)

        self.md5_to_schema[s._md5] = s

        return s

    def add_from_path(self, path=None):
        """
        :param path, is path where there are .toml schema's which will be loaded

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
