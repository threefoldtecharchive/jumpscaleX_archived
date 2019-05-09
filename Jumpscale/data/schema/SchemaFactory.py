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
        self.url_to_md5 = {}  #list inside the dict because there can be more than 1 schema linked to url
        self.url_versionless_to_md5 = {} #list inside the dict because there can be more than 1 schema linked to url

        self.md5_to_schema = {}

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
        self.schemas = {}

    def exists(self, schema_text="", url=None, md5=None):
        md5,schema = self._get(schema_text=schema_text,url=url,md5=md5)
        return schema is not None

    def _get(self,schema_text="", url=None, md5=None):

        if md5 and schema_text:
            if not md5 == self._md5(schema_text):
                raise RuntimeError("md5 is not same as md5 of schema_text: %s-%s"%(md5,self._md5(schema_text)))

        if not md5:
            if schema_text:
                if schema_text.count("@")>1:
                    raise RuntimeError("cannot have multiple blocks in the schema text.\n%s"%schema_text)
                md5 = self._md5(schema_text)
            elif url is not None:
                url = self._urlclean(url)
                if url in self.url_to_md5:
                    md5 = self.url_to_md5[url][-1]
                elif url in self.url_versionless_to_md5:
                    md5 = self.url_versionless_to_md5[url][-1]

        if md5 and md5 in self.md5_to_schema:
            return md5, self.md5_to_schema[md5]

        return md5, None


    def get(self, schema_text="", url=None, md5=None):
        """
        get schema from the url or schema_text or md5

        only supports 1 block

        j.data.schema.get(schema_text="", url=None, md5=None)

        Keyword Arguments:
            schema_text {str} -- schema file path or shcema string  (default: {""})
            url {[type]} -- url of your schema e.g. @url = despiegk.test  (default: {None})
            md5 is the most specific one, if specified will use that one

        Returns:
            Schema
        """

        md5, schema = self._get(schema_text=schema_text,url=url,md5=md5)

        if schema is not None:
            return schema

        #we don't know the schema yet

        if schema_text != "":
            if j.data.types.string.check(schema_text):
                schema = self.add(schema_text=schema_text, url=url, md5=md5)[0]
            else:
                raise RuntimeError("need to be text ")
        else:
            if url is None:
                if md5 is None:
                    raise RuntimeError("cannot have url and md5 None if no schema text specified")
                else:
                    raise RuntimeError("could not find schema with md5: '%s'" % md5)
            elif md5 is None:
                if url is None:
                    raise RuntimeError("cannot have url and md5 None if no schema text specified")
                else:
                    raise RuntimeError("could not find schema '%s'" % url)
            else:
                raise RuntimeError("cannot have url and md5 None if no schema text specified")


        return schema

    def _md5(self, text):
        """
        convert text to md5
        """

        original_text = text.replace(" ", "").replace("\n", "").strip()
        # print("*****\n%s\n***********\n"%(ascii_text))
        return j.data.hash.md5_string(original_text)




    def _urlclean(self,url):
        return url.lower().strip().strip("'\"").strip()


    def _schema_blocks_get(self,schema_text):
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


    def add(self, schema_text, url=None, md5=None):
        """
        :param schema_text can be 1 or more schema's in the text
        when using url or md5 then there can be only 1 schema in the text

        """

        blocks = self._schema_blocks_get(schema_text)

        if len(blocks)>1:
            if url or md5:
                raise RuntimeError("can only use url or md5 if max 1 schema\n%s"%schema_text)
            res = []
            for schema_text in blocks:
                res.append(self.add(schema_text=schema_text)[0])
            return res

        else:
            schema_text = blocks[0]

        md5, schema = self._get(schema_text=schema_text,url=url,md5=md5)

        if schema is not None:
            return [schema]  #did already exist

        if md5 is None:
            md5 = self._md5(schema_text)

        s = Schema(text=schema_text, url=url,md5=md5)

        if s._md5 in self.md5_to_schema:
            raise RuntimeError("should not be there")

        #add md5 to the list if its not there yet
        if not s.url in self.url_to_md5:
            self.url_to_md5[s.url]=[]
        if not s._md5 in self.url_to_md5[s.url]:
            self.url_to_md5[s.url].append(s._md5)

        #add md5 to the list if its not there yet for versionless
        if not s.url_noversion in self.url_versionless_to_md5:
            self.url_versionless_to_md5[s.url_noversion]=[]
        if not s._md5 in  self.url_versionless_to_md5[s.url_noversion]:
             self.url_versionless_to_md5[s.url_noversion].append(s._md5)

        self.md5_to_schema[s._md5] = s

        return [s]

    def test(self, name=""):
        """
        it's run all tests
        js_shell 'j.data.schema.test()'

        if want run specific test ( write the name of test ) e.g. j.data.schema.test(name="base")
        """
        self._test_run(name=name)
