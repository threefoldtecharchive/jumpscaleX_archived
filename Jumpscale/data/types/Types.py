

'''Definition of several primitive type properties (integer, string,...)'''

from .CustomTypes import *
from .CollectionTypes import *
from .PrimitiveTypes import *
from .Enumeration import Enumeration
from .IPAddress import *
from Jumpscale import j


class Types(j.application.JSBaseClass):

    __jslocation__ = "j.data.types"

    def _init(self):
        self.enumerations = {}
        self.ipaddrs = {}

        self._types_list = [Dictionary, List, Guid, Path, Boolean, Integer, Float, String, Bytes, StringMultiLine,
                            IPRange, IPPort, Tel, YAML, JSON, Email, Date, DateTime, Numeric, Percent,
                            Hash, CapnpBin, JSDataObject, JSConfigObject, Url, Enumeration]

        l = []
        for typeclass in self._types_list:
            name = typeclass.NAME.strip().strip("_")
            o = self.__attach(name, typeclass)
            if hasattr(typeclass, "ALIAS"):
                for alias in typeclass.ALIAS.split(","):
                    self.__attach(alias, typeclass,o)

        self._type_check_list = ['guid', 'path', 'multiline', 'iprange', 'ipport',
                                 'tel', 'email', 'date', 'datetime', 'numeric', 'percent', 'hash',
                                 'jsobject', 'url', 'enum',
                                 'dict', 'list', 'boolean', 'integer', 'float', 'string', 'bytes']

        self.enumeration = Enumeration
        self._enumeration = Enumeration()

    def __attach(self, name, typeclass,o=None):
        name = name.strip().lower()
        name2 = "_%s" % name
        self.__dict__[name2] = typeclass
        if o:
            self.__dict__[name] = o
        else:
            self.__dict__[name] = self.__dict__[name2]()
        return self.__dict__[name]

    def type_detect(self, val):
        """
        check for most common types
        """
        for key in self._type_check_list:
            ttype = self.__dict__[key]
            if ttype.check(val):
                return ttype
        raise RuntimeError("did not detect val for :%s" % val)

    def get_custom(self, ttype, **kwargs):
        """
        e.g. for enum, but there can be other types in future who take certain input
        :param ttype:
        :param kwargs: e.g. values="red,blue,green" can also a list for e.g. enum
        :return:

        e.g. for enumeration

        j.data.types.get_custom("e",values="blue,red")

        """
        ttype = ttype.lower().strip()
        if ttype in ["e", "enum"]:
            cl = self._enumeration
            cl = cl.get(values=kwargs["values"])
            self.enumerations[cl._md5] = cl
            return self.enumerations[cl._md5]
        else:
            raise j.exceptions.RuntimeError("did not find custom type:'%s'" % ttype)

    def get(self, ttype):
        """
        type is one of following
        - s, str, string
        - i, int, integer
        - f, float
        - b, bool,boolean
        - tel, mobile
        - d, date
        - t, datetime
        - n, numeric
        - h, hash       #set of 2 int
        - p, percent
        - o, jsobject
        - ipaddr, ipaddress
        - ipport, tcpport
        - iprange
        - email
        - multiline
        - list
        - dict
        - yaml
        - guid
        - url, u
        - e,enum        #enumeration
        """
        ttype = ttype.lower().strip()

        if ttype in ["n", "num", "numeric"]:
            res = self._numeric
        elif ttype.startswith("l"):
            tt = self._list()  # need to create new instance
            if len(ttype) > 1:
                tt.SUBTYPE = self.get(ttype[1:])
                return tt
            elif len(ttype) == 1:
                assert tt.SUBTYPE == None
                return tt

        if not ttype in self._ddict:
            raise j.exceptions.RuntimeError("did not find type:'%s'" % ttype)

        return self.__dict__[ttype]

    def test(self, name=""):
        """
        js_shell 'j.data.types.test()'

        if want run specific test ( write the name of test ) e.g. j.data.schema.test(name="base")
        """
        self._test_run(name=name)

    def fix(self, val, default):
        """
        will convert val to type of default

        separated string goes to [] if default = []

        BE CAREFULL THIS IS A SLOW PROCESS, USE CAREFULLY

        """
        if val is None or val == "" or val == []:
            return default

        if j.data.types.list.check(default):
            res = []
            if j.data.types.list.check(val):
                for val0 in val:
                    if val0 not in res:
                        res.append(val0)
            else:
                val = str(val).replace("'", "")
                if "," in val:
                    val = [item.strip() for item in val.split(",")]
                    for val0 in val:
                        if val0 not in res:
                            res.append(val0)
                else:
                    if val not in res:
                        res.append(val)
        elif j.data.types.bool.check(default):
            if str(val).lower() in ['true', "1", "y", "yes"]:
                res = True
            else:
                res = False
        elif j.data.types.int.check(default):
            res = int(val)
        elif j.data.types.float.check(default):
            res = int(val)
        else:
            res = str(val)
        return res
