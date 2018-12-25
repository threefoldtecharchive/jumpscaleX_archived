import sys
from .List0 import List0
from .Schema import *
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class SchemaFactory(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.data.schema"
        JSBASE.__init__(self)
        self._code_generation_dir = None
        self.db = j.clients.redis.core_get()
        self.schemas = {}
        self._md5_schema = {}

    @property
    def SCHEMA_CLASS(self):
        return Schema

    @property
    def code_generation_dir(self):
        if not self._code_generation_dir:
            path = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "schema")
            j.sal.fs.createDir(path)
            if path not in sys.path:
                sys.path.append(path)
            j.sal.fs.touch(j.sal.fs.joinPaths(path, "__init__.py"))
            self._logger.debug("codegendir:%s" % path)
            self._code_generation_dir = path
        return self._code_generation_dir

    def reset(self):
        self.schemas = {}

    def get(self, schema_text_path="", url=None, die=True):
        """
        get schema from the url or schema_text_path

        Keyword Arguments:
            schema_text_path {str} -- schema file path or shcema string  (default: {""})
            url {[type]} -- url of your schema e.g. @url = despiegk.test  (default: {None})

        Returns:
            Schema
        """

        if schema_text_path != "":
            if j.data.types.string.check(schema_text_path):
                return self._add(schema_text_path)
            else:
                raise RuntimeError("need to be text ")
        else:
            # check is in cash based on url & dbclient
            if url is not None:
                if url in self.schemas:
                    return self.schemas[url]
            raise RuntimeError("could not find schema '%s'" % url)

    def _md5(self, text):
        """
        convert text to md5
        """

        original_text = text.replace(" ", "").replace("\n", "")
        ascii_text = j.core.text.strip_to_ascii_dense(original_text)
        return j.data.hash.md5_string(ascii_text)

    def exists(self, url):
        return self.get(url=url, die=False) is not None

    def _add(self, schema_text_path):
        """
        :param schema_text or schema_path
        :return: incache,schema  (incache is bool, when True means was in cache)
        """

        if "\n" not in schema_text_path:
            if j.sal.fs.exists(schema_text_path):
                schema_text = j.sal.fs.readFile(schema_text_path)
            else:
                raise RuntimeError("this path '%s' doesn't exist" % schema_text_path)
        else:
            schema_text = schema_text_path

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
        res = []
        for block in blocks:
            md5 = self._md5(block)
            if md5 in self._md5_schema:
                res.append(self._md5_schema[md5])
            else:
                s = Schema(text=block)
                if s.md5 in self._md5_schema:
                    raise RuntimeError("should not be there")
                else:
                    res.append(s)
                    self.schemas[s.url] = s

        if len(res) == 0:
            raise RuntimeError("did not find schema in txt")

        return res[0]

    def list_base_class_get(self):
        return List0

    def test(self, name=""):
        """
        it's run all tests
        js_shell 'j.data.schema.test()'

        if want run specific test ( write the name of test ) e.g. j.data.schema.test(name="base")
        """
        self._test_run(name=name)
