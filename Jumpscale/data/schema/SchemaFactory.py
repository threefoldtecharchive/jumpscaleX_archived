
from Jumpscale import j

JSBASE = j.application.JSBaseClass

from .Schema import *
from .List0 import List0
import sys


class SchemaFactory(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.data.schema"
        JSBASE.__init__(self)
        self._template_engine = None
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

        if schema_text_path != "":
            if j.data.types.string.check(schema_text_path):
                return self._add(schema_text_path)
            else:
                raise RuntimeError("need to be text ")
        else:
            #check is in cash based on url & dbclient
            if url is not None:
                if url in self.schemas:
                    return self.schemas[url]
            raise RuntimeError("could not find schema '%s'"%url)

    def _md5(self,text):
        #make sure the md5 is always the same
        t = text.replace(" ","").replace("\n","")
        tt = j.core.text.strip_to_ascii_dense(t)
        return j.data.hash.md5_string(tt)

    def exists(self,url):
        return self.get(url=url, die=False) is not None

    def _add(self, schema_text_path):
        """

        :param schema_text or schema_path
        :return: incache,schema  (incache is bool, when True means was in cache)
        """


        if "\n" not in schema_text_path and j.sal.fs.exists(schema_text_path):
            schema_text = j.sal.fs.readFile(schema_text_path)
        else:
            schema_text = schema_text_path

        block = ""
        blocks=[]
        txt=j.core.text.strip(schema_text)
        for line in txt.split("\n"):

            l=line.lower().strip()

            if block=="":
                if l == "" or l.startswith("#"):
                    continue

            if l.startswith("@url"):
                if block is not "":
                    blocks.append(block)
                    block = ""

            block += "%s\n" % line

        #process last block
        if block is not "":
            blocks.append(block)


        res=[]
        for block in blocks:
            md5=self._md5(block)
            if md5 in self._md5_schema:
                res.append(self._md5_schema[md5])
            else:
                s = Schema(text=block)
                if s.md5 in self._md5_schema:
                    raise RuntimeError("should not be there")
                else:
                    res.append(s)
                    self.schemas[s.url]=s

        if len(res)==0:
            j.shell()
            raise RuntimeError("did not find schema in txt")

        return res[0]

    def list_base_class_get(self):
        return List0

    def test(self):
        """
        js_shell 'j.data.schema.test()'
        """
        self.test1()
        self.test2()
        self.test3()
        self.test4()
        self.test5()

    def test1(self):
        """
        js_shell 'j.data.schema.test1()'
        """
        schema = """
        @url = despiegk.test
        llist2 = "" (LS) #L means = list, S=String        
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 #this is a comment
        llist = []
        llist3 = "1,2,3" (LF)
        llist4 = "1,2,3" (L)
        llist5 = "1,2,3" (LI)
        U = 0.0
        #pool_type = "managed,unmanaged" (E)  #NOT DONE FOR NOW
        """

        s = j.data.schema.get(schema_text_path=schema)

        assert s.url == "despiegk.test"

        print (s)

        o = s.get()

        o.llist.append(1)
        o.llist2.append("yes")
        o.llist2.append("no")
        o.llist3.append(1.2)
        o.llist4.append(1)
        o.llist5.append(1)
        o.llist5.append(2)
        o.U = 1.1
        o.nr = 1
        o.token_price = "10 USD"
        o.description = "something"


        usd2usd = o.token_price_usd # convert USD-to-USD... same value
        assert usd2usd == 10
        inr = o.token_price_cur('inr')
        #print ("convert 10 USD to INR", inr)
        assert inr > 100 # ok INR is pretty high... check properly in a bit...
        eur = o.token_price_eur
        #print ("convert 10 USD to EUR", eur)
        cureur = j.clients.currencylayer.cur2usd['eur']
        curinr = j.clients.currencylayer.cur2usd['inr']
        #print (cureur, curinr, o.token_price)
        assert usd2usd*cureur == eur
        assert usd2usd*curinr == inr

        # try EUR to USD as well
        o.token_price = "10 EUR"
        assert o.token_price == b'\x000\n\x00\x00\x00'
        eur2usd = o.token_price_usd
        assert eur2usd*cureur == 10

        o._cobj

        schema = """
        @url = despiegk.test2
        llist2 = "" (LS)
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 #this is a comment
        llist = []

        @url = despiegk.test3
        llist = []
        description = ""
        """
        j.data.schema.get(schema_text_path=schema)
        s1 = self.get(url="despiegk.test2")
        s2 = self.get(url="despiegk.test3")

        o1 = s1.get()
        o2 = s2.get()
        o2.llist.append("1")

        print("TEST 1 OK")

    def test2(self):
        """
        js_shell 'j.data.schema.test2()'
        """
        schema0 = """
        @url = despiegk.test.group
        description = ""
        llist = "" (LO) !despiegk.test.users
        listnum = "" (LI)
        """

        schema1 = """
        @url = despiegk.test.users
        nr = 4
        date_start = 0 (D)
        description = ""
        token_price = "10 USD" (N)
        cost_estimate:hw_cost = 0.0 (N) #this is a comment
        """

        s1 = self.get(schema1)
        s0 = self.get(schema0)
        print(s0)
        o = s1.get()


        print(s1.capnp_schema)
        print(s0.capnp_schema)
        

        print("TEST 2 OK")


    def test3(self):
        """
        js_shell 'j.data.schema.test3()'

        simple embedded schema

        """
        SCHEMA = """
        @url = jumpscale.schema.test3.cmd
        name = ""
        comment = ""
        schemacode = ""

        @url = jumpscale.schema.test3.serverschema
        cmds = (LO) !jumpscale.schema.test3.cmdbox

        @url = jumpscale.schema.test3.cmdbox
        @name = GedisServerCmd1
        cmd = (O) !jumpscale.schema.test3.cmd
        cmd2 = (O) !jumpscale.schema.test3.cmd
        
        """
        self.get(SCHEMA)
        s2 = self.get(url="jumpscale.schema.test3.serverschema")
        s3 = self.get(url="jumpscale.schema.test3.cmdbox")

        o = s2.get()
        for i in range(4):
            oo = o.cmds.new()
            oo.name = "test%s"%i

        assert o.cmds[2].name=="test2" 
        o.cmds[2].name="testxx"
        assert o.cmds[2].name=="testxx" 

        bdata = o._data

        o2 = s2.get(capnpbin=bdata)

        assert o._ddict == o2._ddict

        print (o._data)

        o3 = s3.get()
        o3.cmd.name = "test"
        o3.cmd2.name = "test"
        assert o3.cmd.name == "test"
        assert o3.cmd2.name == "test"

        bdata = o3._data
        o4 = s3.get(capnpbin=bdata)
        assert o4._ddict == o3._ddict

        assert o3._data == o4._data


        print("TEST 3 OK")

    def test4(self):
        """
        js_shell 'j.data.schema.test4()'

        tests an issue with lists, they were gone at one point after setting a value

        test readonly behaviour

        """

        S0 = """
        @url = jumpscale.schema.test3.cmd
        name = ""
        comment = ""        
        nr = 0
        """
        self.get(S0)

        SCHEMA = """
        @url = jumpscale.myjobs.job
        category*= ""
        time_start* = 0 (D)
        time_stop = 0 (D)
        state* = ""
        timeout = 0
        action_id* = 0
        args = ""   #json
        kwargs = "" #json
        result = "" #json
        error = ""
        return_queues = (LS)
        cmds = (LO) !jumpscale.schema.test3.cmd
        cmd = (O) !jumpscale.schema.test3.cmd
        
        """
        s = self.get(SCHEMA)
        o = s.new()
        o.return_queues = ["a", "b"]
        assert o._return_queues.pylist() == ["a", "b"]
        assert o._return_queues._inner_list == ["a", "b"]
        assert o.return_queues == ["a", "b"]

        o.return_queues[1] = "c"
        assert o._return_queues.pylist() == ["a", "c"]
        assert o._return_queues._inner_list == ["a", "c"]
        assert o.return_queues == ["a", "c"]

        o.return_queues.pop(0)
        assert o._return_queues.pylist() == ["c"]
        assert o._return_queues._inner_list == ["c"]
        assert o.return_queues == ["c"]

        cmd = o.cmds.new()
        cmd.name = "aname"
        cmd.comment = "test"
        cmd.nr = 10

        o.cmd.name = "aname2"
        o.cmd.nr = 11

        o.category = "acategory"

        o1 = {'category': 'acategory',
                 'time_start': 0,
                 'time_stop': 0,
                 'state': '',
                 'timeout': 0,
                 'action_id': 0,
                 'args': '',
                 'kwargs': '',
                 'result': '',
                 'error': '',
                 'cmd': {'name': 'aname2', 'comment': '', 'nr': 11},
                 'return_queues': ['c'],
                 'cmds': [{'name': 'aname', 'comment': 'test', 'nr': 10}]}


        assert o._ddict == o1

        o._data
        o._json

        assert o._ddict == o1

        o2 = s.get(capnpbin= o._data)

        assert o._ddict == o2._ddict
        assert o._data == o2._data

        assert o.readonly==False
        o.readonly = True

        #test we cannot change a subobj
        try:
            o.category = "s"
        except Exception as e:
            assert str(e).find("object readonly, cannot set")!=-1

        #THERE IS STILL ERROR, readonly does not work for subobjects, need to change template


        print ("TEST4 ok")

    def test5(self):
        """
        js_shell 'j.data.schema.test5()'

        test loading of data from toml source

        """

        toml = """
        enable = true
        #unique name with dot notation for the package
        name = "digitalme.base"
        
        
        [[loaders]]
        giturl = "https://github.com/threefoldtech/digital_me/tree/development960/packages/system/base"
        dest = ""
        
        [[loaders]]
        giturl = "https://github.com/threefoldtech/jumpscale_weblibs/tree/master/static"
        dest = "blueprints/base/static"

        """

        SCHEMA_PACKAGE = """
        @url =  jumpscale.digitalme.package
        name = "UNKNOWN" (S)           #official name of the package, there can be no overlap (can be dot notation)
        enable = true (B)
        args = (LO) !jumpscale.digitalme.package.arg
        loaders= (LO) !jumpscale.digitalme.package.loader
        
        @url =  jumpscale.digitalme.package.arg
        key = "" (S)
        val =  "" (S)
        
        @url =  jumpscale.digitalme.package.loader
        giturl =  "" (S)
        dest =  "" (S)
        enable = true (B)
        
        ##ENDSCHEMA

        """

        data = j.data.serializers.toml.loads(toml)

        s=j.data.schema.get(SCHEMA_PACKAGE)
        data = s.get(data=data)

        assert j.core.text.strip_to_ascii_dense(str(data)) == '_args_enable_true_loaders_dest_enable_true_giturl_https_github.com_threefoldtech_digital_me_tree_development960_packages_system_base_dest_blueprints_base_static_enable_true_giturl_https_github.com_threefoldtech_jumpscale_weblibs_tree_master_static_name_digitalme.base'



        print ("TEST 5 ok")
