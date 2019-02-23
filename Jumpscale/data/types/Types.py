

'''Definition of several primitive type properties (integer, string,...)'''

from .CustomTypes import *
from .CollectionTypes import *
from .PrimitiveTypes import *
from .Enumeration import Enumeration
from .IPAddress import *
from Jumpscale import j
import copy

class Custom(j.application.JSBaseClass):
    def _init(self):
        self._types = {}

class Types(j.application.JSBaseClass):

    __jslocation__ = "j.data.types"

    def _init(self):

        self._types_list = [Dictionary, List, Guid, Path, Boolean, Integer, Float, String, Bytes, StringMultiLine,
                            IPRange, IPPort, Tel, YAML, JSON, Email, Date, DateTime, Numeric, Percent,
                            Hash, CapnpBin, JSDataObject, JSConfigObject, Url, Enumeration]

        self.custom = Custom()

        self._type_check_list = []
        for typeclass in self._types_list:
            name = typeclass.NAME.strip().strip("_").lower()
            if "," in name:
                aliases = [name.strip() for name in name.split(",")]
                name=aliases[0]
                aliases.pop(aliases.index(name))
            else:
                aliases = None
            o = self.__attach(name, typeclass)
            if name in self._type_check_list:
                raise RuntimeError("there is duplicate type:%s"%name)
            if not hasattr(o,"NOCHECK") or o.NOCHECK is False:
                self._type_check_list.append(name)
            if aliases:
                for alias in aliases:
                    self.__attach(alias, typeclass,o)

    def __attach(self, name, typeclass,o=None):
        name = name.strip().lower()
        name2 = "_%s" % name

        if not hasattr(typeclass,"CUSTOM") or typeclass.CUSTOM is False:
            #o is the object
            if not o:
                o = typeclass()
                o._jsx_location = "j.data.types.%s"%name

        if hasattr(typeclass,"CUSTOM") and typeclass.CUSTOM is True:
            self.custom.__dict__[name] = typeclass  #only attach class
        else:
            self.__dict__[name] = o
            self.__dict__[name2] = typeclass

        return o

    def type_detect(self, val):
        """
        check for most common types
        """
        for key in self._type_check_list:
            ttype = self.__dict__[key]
            if ttype.check(val):
                return ttype
        raise RuntimeError("did not detect val for :%s" % val)


    def get(self, ttype,default=None):
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


        :param default: e.g. "red,blue,green" for an enumerator
            for certain types e.g. enumeration the default value is needed to create the right type

        """
        ttype = ttype.lower().strip()

        if ttype.startswith("l"):
            default_copy=copy.copy(default)
            if len(ttype) > 1:
                default = ttype[1:]
            elif len(ttype) == 1:
                default = None
            else:
                raise RuntimeError("list type can only be 1 or 2 chars")

        if ttype in self.custom.__dict__:
            tt_class = self.custom.__dict__[ttype]  #is the class
            name = tt_class.NAME.split(",")[0]
            key0=default.replace(" ","").replace(",","_")
            key="%s_%s"%(name,key0)
            tt = tt_class(default)
            self.custom._types[key] = tt
            tt._jsx_location = "j.data.types.custom._types['%s']"%key
            if ttype.startswith("l"):
                #is a list, copy default values in
                tt._default_values = tt.fromString(default_copy)
            return tt
        elif ttype in self.__dict__:
            tt = self.__dict__[ttype]
            return tt
        else:
            raise j.exceptions.RuntimeError("did not find type:'%s'" % ttype)





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
