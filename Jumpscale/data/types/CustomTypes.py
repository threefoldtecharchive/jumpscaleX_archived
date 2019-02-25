""" Definition of several custom types (paths, ipaddress, guid,...)
"""

import re
import struct
import builtins
from .PrimitiveTypes import String, Integer
import copy
import time
from uuid import UUID
from Jumpscale import j
from datetime import datetime
from .TypeBaseClasses import *


class Guid(String):
    '''
    Generic GUID type
    stored as binary internally
    '''

    NAME =  'guid'

    def __init__(self):
        self.BASETYPE = "string"

    def check(self, value):
        try:
            val = UUID(value, version=4)
        except (ValueError, AttributeError):
            return False
        return val.hex == value.replace('-', '')

    def default_get(self):
        return j.data.idgenerator.generateGUID()

    def fromString(self, v):
        if not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
        if self.check(v):
            return v
        else:
            raise ValueError("%s not properly formatted: '%s'" % (Guid.NAME, v))

    toString = fromString


class Email(String):
    """
    """
    NAME =  'email'

    def __init__(self):
        self.BASETYPE = "string"
        self._RE = re.compile('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def check(self, value):
        '''
        Check whether provided value is a valid tel nr
        '''
        if not j.data.types.string.check(value):
            return False
        return self._RE.fullmatch(value) is not None

    def clean(self, v):
        v = j.data.types.string.clean(v)
        if not self.check(v):
            raise ValueError("Invalid email :%s" % v)
        v = v.lower()
        return v


class Path(String):
    '''Generic path type'''
    NAME =  'path'

    def __init__(self):
        self.BASETYPE = "string"
        self._RE = re.compile("^(?:\.{2})?(?:\/\.{2})*(\/[a-zA-Z0-9]+)+$")

    def check(self, value):
        '''
        Check whether provided value is a valid
        '''
        return self._RE.fullmatch(value) is not None

    def default_get(self):
        return ""


class Url(String):
    '''Generic url type'''
    NAME =  'url,u'

    def __init__(self):
        self.BASETYPE = "string"
        self._RE = re.compile(
            "(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,}")

    def check(self, value):
        '''
        Check whether provided value is a valid
        '''
        return self._RE.fullmatch(value) is not None


class Tel(String):
    """
    format is e.g. +32 475.99.99.99x123
    only requirement is it needs to start with +
    the. & , and spaces will not be remembered
    and x stands for phone number extension
    """
    NAME =  'tel,mobile'

    def __init__(self):
        self.BASETYPE = "string"
        self._RE = re.compile('^\+?[0-9]{6,15}(?:x[0-9]+)?$')

    def check(self, value):
        '''
        Check whether provided value is a valid
        '''
        return self._RE.fullmatch(value) is not None

    def clean(self, v):

        v = j.data.types.string.clean(v)
        v = v.replace(".", "")
        v = v.replace(",", "")
        v = v.replace("-", "")
        v = v.replace("(", "")
        v = v.replace(")", "")
        v = v.replace(" ", "")
        if not self.check(v):
            raise ValueError("Invalid mobile number :%s" % v)
        return v

class IPRange(String):
    """
    """
    NAME =  'iprange'

    def __init__(self):
        self.BASETYPE = "string"
        self._RE = re.compile('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}')

    def check(self, value):
        '''
        Check whether provided value is a valid
        '''
        return self._RE.fullmatch(value) is not None

class IPPort(Integer):
    '''Generic IP port type'''
    NAME =  'ipport,tcpport'

    def __init__(self):
        self.BASETYPE = "string"
        self.NOCHECK = True

    def default_get(self):
        return 65535


    def possible(self, value):
        '''
        Check if the value is a valid port
        We just check if the value a single port or a range
        Values must be between 0 and 65535
        '''
        try:
            if 0 < int(value) <= 65535:
                return True
        except :
            pass
        return False


class NumericObject(TypeBaseObjClassNumeric):


    @property
    def _string(self):
        return self._typebase.bytes2str(self._data)

    @property
    def _python_code(self):
        return "'%s'"%self._string

    @property
    def usd(self):
        return self._value

    @property
    def value(self):
        return self._typebase.bytes2cur(self._data)

    @value.setter
    def value(self,val):
        self._data = self._typebase.toData(val)


class Numeric(TypeBaseObjFactory):
    """
    has support for currencies and does nice formatting in string

    storformat = 6 or 10 bytes (10 for float)

    will return int as jumpscale basic implementation

    """
    NAME =  'numeric,n'

    def __init__(self):
        TypeBaseObjFactory.__init__(self)

        self.NOCHECK = True


    def bytes2cur(self, bindata, curcode="usd", roundnr=None):

        if bindata in [b'',None]:
            return 0

        if len(bindata) not in [6, 10]:
            raise j.exceptions.Input("len of data needs to be 6 or 10")

        ttype = struct.unpack("B", builtins.bytes([bindata[0]]))[0]
        curtype0 = struct.unpack("B", builtins.bytes([bindata[1]]))[0]

        if ttype > 127:
            ttype = ttype - 128
            negative = True
        else:
            negative = False

        if ttype == 1:
            val = struct.unpack("d", bindata[2:])[0]
        else:
            val = struct.unpack("I", bindata[2:])[0]

        if ttype == 10:
            val = val * 1000
        elif ttype == 11:
            val = val * 1000000
        elif ttype == 2:
            val = round(float(val) / 10000, 3)
            if int(float(val)) == val:
                val = int(val)

        # if curtype0 not in j.clients.currencylayer.id2cur:
        #     raise RuntimeError("need to specify valid curtype, was:%s"%curtype)
        currency = j.clients.currencylayer
        curcode0 = currency.id2cur[curtype0]
        if not curcode0 == curcode:
            val = val / currency.cur2usd[curcode0]  # val now in usd
            val = val * currency.cur2usd[curcode]

        if negative:
            val = -val

        if roundnr:
            val = round(val, roundnr)

        return val

    def bytes2str(self, bindata, roundnr=8, comma=True):
        if len(bindata) == 0:
            bindata = self.default_get()

        elif len(bindata) not in [6, 10]:
            raise j.exceptions.Input("len of data needs to be 6 or 10")

        ttype = struct.unpack("B", builtins.bytes([bindata[0]]))[0]
        curtype = struct.unpack("B", builtins.bytes([bindata[1]]))[0]

        if ttype > 127:
            ttype = ttype - 128
            negative = True
        else:
            negative = False

        if ttype == 1:
            val = struct.unpack("d", bindata[2:])[0]
        else:
            val = struct.unpack("I", bindata[2:])[0]

        if ttype == 10:
            mult = "k"
        elif ttype == 11:
            mult = "m"
        elif ttype == 2:
            mult = "%"
            val = round(float(val) / 100, 2)
            if int(val) == val:
                val = int(val)
        else:
            mult = ""
        currency = j.clients.currencylayer
        if curtype is not currency.cur2id["usd"]:
            curcode = currency.id2cur[curtype]
        else:
            curcode = ""

        if comma:
            out = str(val)
            if "." not in out:
                val = ""
                while len(out) > 3:
                    val = "," + out[-3:] + val
                    out = out[:-3]
                val = out + val
                val = val.strip(",")

        if negative:
            res = "-%s %s%s" % (val, mult, curcode.upper())
        else:
            res = "%s %s%s" % (val, mult, curcode.upper())
        res = res.replace(" %", "%")
        # print(res)
        return res.strip()

    def getCur(self, value):
        value = value.lower()
        for cur2 in list(j.clients.currencylayer.cur2usd.keys()):
                # print(cur2)
            if value.find(cur2) != -1:
                    # print("FOUND:%s"%cur2)
                value = value.lower().replace(cur2, "").strip()
                return value, cur2
        cur2 = "usd"
        return value, cur2

    def str2bytes(self, value):
        """

        US style: , is for 1000  dot(.) is for floats

        value can be 10%,0.1,100,1m,1k  m=million
        USD/EUR/CH/EGP/GBP are understood (+- all currencies in world)

        e.g.: 10%
        e.g.: 10EUR or 10 EUR (spaces are stripped)
        e.g.: 0.1mEUR or 0.1m EUR or 100k EUR or 100000 EUR

        j.tools.numtools.text2num_bytes("0.1mEUR")

        j.tools.numtools.text2num_bytes("100")
        if not currency symbol specified then will default to usd

        bytes format:

        $type:1byte + $cur:1byte + $4byte value (int or float)

        $type:
        last 4 bytes:
        - 0: int, no multiplier
        - 1: float, no multiplier
        - 2: int, percent (expressed as 1-10000, so 100% = 10000, 1%=100)
        - 3: was float but expressed as int because is bigger than 10000 (no need to keep float part)
        - 10: int, multiplier = 1000
        - 11: int, multiplier = 1000000

        first bit:
        - True if neg nr, otherwise pos nr (in other words if nr < 128 then pos nr)

        see for codes in:
        - j.clients.currencylayer.cur2id
        - j.clients.currencylayer.id2cur

        """

        if not j.data.types.string.check(value):
            raise j.exceptions.RuntimeError("value needs to be string in text2val, here: %s" % value)

        if "," in value:  # is only formatting in US
            value = value.replace(",", "").lstrip(",").strip()

        if "-" in value:
            negative = True
            value = value.replace("-", "").lstrip("-")
        else:
            negative = False

        try:
            # dirty trick to see if value can be float, if not will look for currencies
            v = float(value)
            cur2 = "usd"
        except ValueError as e:
            cur2 = None

        if cur2 is None:
            value, cur2 = self.getCur(value)

        if value.find("k") != -1:
            value = value.replace("k", "").strip()
            if "." in value:
                value = int(float(value) * 1000)
                ttype = 0
            else:
                value = int(value)
                ttype = 10
        elif value.find("m") != -1:
            value = value.replace("m", "").strip()
            if "." in value:
                value = int(float(value) * 1000)
                ttype = 10
            else:
                value = int(value)
                ttype = 11
        elif value.find("%") != -1:
            value = value.replace("%", "").strip()
            value = int(float(value) * 100)
            ttype = 2
        else:
            if value.strip() == "":
                value = "0"
            fv = float(value)
            if fv.is_integer():  # check floated val fits into an int
                # ok, we now know str->float->int will actually be an int
                value = int(fv)
                ttype = 0
            else:
                value = fv
                if fv > 10000:
                    value = int(value)  # doesn't look safe.  issue #72
                    ttype = 3
                else:
                    ttype = 1
        currency = j.clients.currencylayer
        curcat = currency.cur2id[cur2]

        if negative:
            ttype += 128

        if ttype == 1 or ttype == 129:
            return struct.pack("B", ttype) + struct.pack("B", curcat) + struct.pack("d", value)
        else:
            return struct.pack("B", ttype) + struct.pack("B", curcat) + struct.pack("I", value)

    def clean(self, data):
        if isinstance(data,NumericObject):
            return data
        return NumericObject(self,data)

    def toData(self,data):
        # print("num:clean:%s"%data)
        if j.data.types.string.check(data):
            data = j.data.types.string.clean(data)
            data = self.str2bytes(data)
        elif j.data.types.bytes.check(data):
            if len(data) not in [6, 10]:
                raise j.exceptions.Input("len of numeric bytes needs to be 6 or 10 bytes")
        elif isinstance(data,int) or isinstance(data,float):
            data = self.str2bytes(str(data))
        else:
            raise RuntimeError("could not clean data, did not find supported type:%s"%data)

        return data


class DateTime(Integer):
    '''
    internal representation is an epoch (int)
    '''
    NAME =  'datetime,t'

    def __init__(self):

        self.BASETYPE = "int"
        self.NOCHECK = True

        # self._RE = re.compile('[0-9]{4}/[0-9]{2}/[0-9]{2}')  #something wrong here is not valid for time

    def default_get(self):
        return 0

    def fromString(self, txt):
        return self.clean(txt)

    def toString(self, val, local=True):
        val = self.clean(val)
        if val == 0:
            return ""
        return j.data.time.epoch2HRDateTime(val, local=local)

    def toHR(self, v):
        return self.toString(v)

    def clean(self, v):
        """
        support following formats:
        - None, 0: means undefined date
        - epoch = int
        - month/day 22:50
        - month/day  (will be current year if specified this way)
        - year(4char)/month/day
        - year(4char)/month/day 10am:50
        - year(2char)/month/day
        - day/month/4char
        - year(4char)/month/day 22:50
        - +4h
        - -4h
        in stead of h also supported: s (second) ,m (min) ,h (hour) ,d (day),w (week), M (month), Y (year)

        will return epoch

        """
        def date_process(dd):
            if "/" not in dd:
                raise j.exceptions.Input("date needs to have:/, now:%s" % v)
            splitted = dd.split("/")
            if len(splitted) == 2:
                dfstr = "%Y/%m/%d"
                dd = "%s/%s" % (j.data.time.epoch2HRDate(j.data.time.epoch).split("/")[0], dd.strip())
            elif len(splitted) == 3:
                s0 = splitted[0].strip()
                s1 = splitted[1].strip()
                s2 = splitted[2].strip()
                if len(s0) == 4 and (len(s1) == 2 or len(s1) == 1) and (len(s2) == 2 or len(s2) == 1):
                    # year in front
                    dfstr = "%Y/%m/%d"
                elif len(s2) == 4 and (len(s1) == 2 or len(s1) == 1) and (len(s0) == 2 or len(s0) == 1):
                    # year at end
                    dfstr = "%d/%m/%Y"
                elif (len(s2) == 2 or len(s2) == 1) and (len(s1) == 2 or len(s1) == 1) and (len(s0) == 2 or len(s0) == 1):
                    # year at start but small
                    dfstr = "%y/%m/%d"
                else:
                    raise j.exceptions.Input("date wrongly formatted, now:%s" % v)
            else:
                raise j.exceptions.Input("date needs to have 2 or 3 /, now:%s" % v)
            return (dd, dfstr)

        def time_process(v):
            v = v.strip()
            if ":" not in v:
                return ("00:00:00", "%H:%M:%S")
            splitted = v.split(":")
            if len(splitted) == 2:
                if "am" in v.lower() or "pm" in v.lower():
                    fstr = "%I%p:%M"
                else:
                    fstr = "%H:%M"
            elif len(splitted) == 3:
                if "am" in v.lower() or "pm" in v.lower():
                    fstr = "%I%p:%M:%S"
                else:
                    fstr = "%H:%M:%S"
            return (v, fstr)
        
        if v is None:
            v=0

        if j.data.types.string.check(v):
            v=v.replace("'","").replace("\"","").strip()
            if v.strip() in ["0", "",0]:
                return 0

            if "+" in v or "-" in v:
                return j.data.time.getEpochDeltaTime(v)

            if ":" in v:
                # have time inside the representation
                dd, tt = v.split(" ", 1)
                tt, tfstr = time_process(tt)
            else:
                tt, tfstr = time_process("")
                dd = v

            dd, dfstr = date_process(dd)

            fstr = dfstr + " " + tfstr
            hrdatetime = dd + " " + tt
            epoch = int(time.mktime(time.strptime(hrdatetime, fstr)))
            return epoch
        elif j.data.types.int.check(v):
            return v
        else:
            raise ValueError("Input needs to be string:%s" % v)

    def capnp_schema_get(self, name, nr):
        return "%s @%s :UInt32;" % (name, nr)

    def test(self):
        """
        js_shell 'j.data.types.datetime.test()'
        """


class Date(DateTime):
    '''
    internal representation is an epoch (int)
    '''
    NAME =  'date,d'

    def __init__(self):

        self.BASETYPE = "int"
        # self._RE = re.compile('[0-9]{4}/[0-9]{2}/[0-9]{2}')
        self.NOCHECK = True

    def clean(self, v):
        """
        support following formats:
        - 0: means undefined date
        - epoch = int  (will round to start of the day = 00h)
        - month/day  (will be current year if specified this way)
        - year(4char)/month/day
        - year(2char)/month/day
        - day/month/4char
        - +4M
        - -4Y
        in stead of h also supported: s (second) ,m (min) ,h (hour) ,d (day),w (week), M (month), Y (year)

        will return epoch

        """
        if isinstance(v,str):
            v=v.replace("'","").replace("\"","").strip()
        if v in [0,"0",None,""]:
            return 0
        # am sure there are better ways how to do this but goes to beginning of day
        v2 = DateTime.clean(self,v)
        dt = datetime.fromtimestamp(v2)
        dt2 = datetime(dt.year,dt.month,dt.day,0,0)
        return int(dt2.strftime('%s'))

    def toString(self, val, local=True):
        val = self.clean(val)
        if val == 0:
            return ""
        return j.data.time.epoch2HRDate(val, local=local)

