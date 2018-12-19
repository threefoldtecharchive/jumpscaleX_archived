""" Definition of several custom types (paths, ipaddress, guid,...)
"""

import re
import struct
import builtins
from .PrimitiveTypes import String, Integer
import copy
import time
from uuid import UUID
from ipaddress import IPv4Address, IPv6Address
from ipaddress import AddressValueError, NetmaskValueError
from Jumpscale import j


class Guid(String):
    '''
    Generic GUID type
    stored as binary internally
    '''

    NAME = 'guid'

    def __init__(self):
        String.__init__(self)

    def check(self, value):
        ''' Check whether provided value is a valid GUID string
            (WITHOUT using insane regular expressions.  also catches
             INVALID uuid4 which would otherwise be valid hex strings
             https://gist.github.com/ShawnMilo/7777304)
        '''
        try:
            val = UUID(value, version=4)
        except (ValueError, AttributeError):
            return False
        return val.hex == value.replace('-', '')

    def get_default(self):
        return j.data.idgenerator.generateGUID()

    def fromString(self, v):
        if not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
        if self.check(v):
            return v
        else:
            raise ValueError("%s not properly formatted: '%s'" %
                             (Guid.NAME, v))

    toString = fromString


class Email(String):
    """
    """

    NAME = 'email'

    def __init__(self):
        String.__init__(self)

        self._RE = re.compile(
            '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    def check(self, value):
        '''
        Check whether provided value is a valid tel nr
        '''
        if not j.data.types.string.check(value):
            return False
        value = self.clean(value)
        return self._RE.fullmatch(value) is not None

    def clean(self, v):
        if not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
        v = v.lower()
        v.strip()
        return v

    def fromString(self, v):
        v = self.clean(v)
        if self.check(v):
            return v
        else:
            raise ValueError("%s not properly formatted: '%s'" %
                             (self.NAME, v))

    toString = fromString

    def get_default(self):
        return "changeme@example.com"


class Path(String):
    '''Generic path type'''
    NAME = 'path'

    def __init__(self):
        String.__init__(self)
        self._RE = re.compile('.*')

    def get_default(self):
        return ""


class Url(String):
    '''Generic url type'''
    NAME = 'url'

    def __init__(self):
        String.__init__(self)
        self._RE = re.compile('.*')

    def get_default(self):
        return ""


class Tel(String):
    """
    format is e.g. +32 475.99.99.99x123
    only requirement is it needs to start with +
    the. & , and spaces will not be remembered
    and x stands for phone number extension
    """
    NAME = 'tel'

    def __init__(self):
        String.__init__(self)
        self._RE = re.compile('^\+?[0-9]{6,15}(?:x[0-9]+)?$')

    def clean(self, v):
        if not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
        v = v.replace(".", "")
        v = v.replace(",", "")
        v = v.replace("-", "")
        v = v.replace("(", "")
        v = v.replace(")", "")
        v = v.replace(" ", "")
        v.strip()
        return v

    def get_default(self):
        return "+32 475.99.99.99"


class IPRange(String):
    """
    """
    NAME = 'iprange'

    def __init__(self):
        String.__init__(self)
        self._RE = re.compile(
            '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}')

    def get_default(self):
        return "192.168.1.1/24"


class IPAddress(String):
    """
    """
    NAME = 'ipaddr'

    def __init__(self):
        String.__init__(self)
        self._RE = re.compile('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')

    def get_default(self):
        return "192.168.1.1"

    def check(self, ip):
        """Validates IP addresses.
        """
        return self.is_valid_ipv4(ip) or self.is_valid_ipv6(ip)

    def is_valid_ipv4(self, ip):
        """ Validates IPv4 addresses.
            https://stackoverflow.com/questions/319279/
            the use of regular expressions is INSANE. and also wrong.
            use standard python3 ipaddress module instead.
        """
        try:
            return IPv4Address(ip) and True
        except (AddressValueError, NetmaskValueError):
            return False

    def is_valid_ipv6(self, ip):
        """ Validates IPv6 addresses.
            https://stackoverflow.com/questions/319279/
            the use of regular expressions is INSANE. and also wrong.
            use standard python3 ipaddress module instead.
        """
        try:
            return IPv6Address(ip) and True
        except (AddressValueError, NetmaskValueError):
            return False


class IPPort(Integer):
    '''Generic IP port type'''
    NAME = 'ipport'

    def __init__(self):
        Integer.__init__(self)
        self.BASETYPE = 'string'

    def check(self, value):
        '''
        Check if the value is a valid port
        We just check if the value a single port or a range
        Values must be between 0 and 65535
        '''
        if not Integer.check(self, value):
            return False
        if 0 < value <= 65535:
            return True
        return False


class Numeric(String):
    """
    has support for currencies and does nice formatting in string

    storformat = 6 or 10 bytes (10 for float)

    """
    NAME = 'numeric'

    def __init__(self):
        String.__init__(self)

    def get_default(self):
        return self.str2bytes("0 USD")

    def capnp_schema_get(self, name, nr):
        """
        is 5 bytes, 1 for type, 4 for float value
        - j.clients.currencylayer.cur2id
        - j.clients.currencylayer.id2cur

        struct.pack("B",1)+struct.pack("f",1234234234.0)

        """
        return "%s @%s :Data;" % (name, nr)

    def bytes2cur(self, bindata, curcode="usd", roundnr=None):
        if bindata == b'':
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

        curcode0 = j.clients.currencylayer.id2cur[curtype0]
        if not curcode0 == curcode:
            val = val / j.clients.currencylayer.cur2usd[curcode0]  # val now in usd
            val = val * j.clients.currencylayer.cur2usd[curcode]

        if negative:
            val = -val

        if roundnr:
            val = round(val, roundnr)

        return val

    def bytes2str(self, bindata, roundnr=8, comma=True):
        if len(bindata) == 0:
            bindata = self.get_default()

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

        if curtype is not j.clients.currencylayer.cur2id["usd"]:
            curcode = j.clients.currencylayer.id2cur[curtype]
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
        except Exception as e:
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
            if fv.is_integer(): # check floated val fits into an int
                # ok, we now know str->float->int will actually be an int
                value = int(fv)
                ttype = 0
            else:
                value = fv
                if fv > 10000:
                    value = int(value) # doesn't look safe.  issue #72
                    ttype = 3
                else:
                    ttype = 1
        curcat = j.clients.currencylayer.cur2id[cur2]

        if negative:
            ttype += 128

        if ttype == 1 or ttype == 129:
            return struct.pack("B", ttype) + struct.pack("B", curcat) + struct.pack("d", value)
        else:
            return struct.pack("B", ttype) + struct.pack("B", curcat) + struct.pack("I", value)

    def test(self):
        """
        js_shell 'j.data.types.numeric.test()'
        """

        assert self.bytes2str(self.str2bytes("123456789")) == "123,456,789"
        assert self.bytes2str(self.str2bytes("100000")) == "100,000"
        assert self.bytes2str(self.str2bytes("10000")) == "10,000"
        assert self.bytes2str(self.str2bytes("1000")) == "1,000"
        assert self.bytes2str(self.str2bytes("100")) == "100"

        assert self.bytes2cur(self.str2bytes("10usd"), "eur") < 10
        assert self.bytes2cur(self.str2bytes("10usd"), "eur") > 7
        assert self.bytes2cur(self.str2bytes("10eur"), "eur") == 10
        assert self.bytes2cur(self.str2bytes("10.3eur"), "eur") == 10.3
        assert self.bytes2cur(self.str2bytes("10eur"), "usd") > 10
        assert self.bytes2cur(self.str2bytes("10eur"), "usd") < 15

        assert self.bytes2str(self.str2bytes("10")) == "10"
        assert self.bytes2str(self.str2bytes("10 USD")) == "10"
        assert self.bytes2str(self.str2bytes("10 usd")) == "10"
        assert self.bytes2str(self.str2bytes("10 eur")) == "10 EUR"
        assert self.bytes2str(self.str2bytes("10 keur")) == "10 kEUR"
        assert self.bytes2str(self.str2bytes("10.1 keur")) == "10,100 EUR"
        assert self.bytes2str(self.str2bytes("10,001 eur")) == "10,001 EUR"
        assert self.bytes2str(self.str2bytes("10,001 keur")) == "10,001 kEUR"
        assert self.bytes2str(self.str2bytes("10,001.01 keur")) == "10,001,010 EUR"
        assert self.bytes2str(self.str2bytes("10,001.01 k")) == "10,001,010"
        assert self.bytes2str(self.str2bytes("-10,001.01 k")) == "-10,001,010"
        assert self.bytes2str(self.str2bytes("0.1%")) == "0.1%"
        assert self.bytes2str(self.str2bytes("1%")) == "1%"
        assert self.bytes2str(self.str2bytes("150%")) == "150%"
        assert self.bytes2str(self.str2bytes("-150%")) == "-150%"
        assert self.bytes2str(self.str2bytes("0.001")) == "0.001"
        assert self.bytes2str(self.str2bytes("0.001 eur")) == "0.001 EUR"
        assert self.bytes2str(self.str2bytes("-0.1 eur")) == "-0.1 EUR"
        # assert self.bytes2str(self.str2bytes(("-0.0001"))=="-0.0001"
        # assert self.bytes2cur(self.str2bytes("0.001usd"),"usd") == 1
        # assert self.bytes2cur(self.str2bytes("0.001k"),"usd") == 0.001

        # print (self.bytes2cur(self.str2bytes("0.001k"),"eur"))
        # from IPython import embed;embed(colors='Linux')

        # test that encoding currencies that fit in an int are only
        # 6 bytes (1 for type, 1 for currency code, 4 for int)
        # and those that fit into a float are 10 bytes
        # (1 for type, 1 for currency code, 8 for float)
        assert len(self.str2bytes("10 usd")) == 6
        assert len(self.str2bytes("10.0 usd")) == 6
        assert len(self.str2bytes("10.1 usd")) == 10

    def clean(self, data):
        # print("num:clean:%s"%data)
        if j.data.types.string.check(data):
            data = data.strip().strip("'").strip("\"").strip()
            return self.str2bytes(data)
        elif j.data.types.bytes.check(data):
            return data
        else:
            return self.str2bytes("%s USD" % data)

    def fromString(self, txt):
        return self.clean(txt)

    def toHR(self, v):
        return self.toString(v)

    def toJSON(self,v):
        return self.toString(v)

    def toString(self, val):
        if val == 0:
            return ""
        if j.data.types.string.check(val):
            return val
        elif j.data.types.bytes.check(val):
            return self.bytes2str(val)
        else:
            return "%s USD" % val

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        value = self.clean(value)
        return "'%s'" % self.toString(value)


class Date(String):
    '''
    internal representation is an epoch (int)
    '''
    NAME = 'date'

    def __init__(self):
        String.__init__(self)
        self._RE = re.compile('[0-9]{4}/[0-9]{2}/[0-9]{2}')

    def get_default(self):
        return 0

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        return self.clean(value)

    def check(self, value):
        '''
        Check whether provided value is a valid date/time representation
        be carefull is SLOW
        '''
        try:
            self.clean(value)
            return True
        except:
            return False

    def fromString(self, txt):
        return self.clean(txt)

    def toString(self, val, local=True):
        val = self.clean(val)
        if val==0:
            return ""
        return j.data.time.epoch2HRDateTime(val, local=local)

    def toHR(self, v):
        return self.toString(v)

    def clean(self, v):
        """
        support following formats:
        - 0: means undefined date
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
        in stead of h also supported: s (second) ,m (min) ,h (hour) ,d (day),w (week)
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
                if len(s0) == 4 and len(s1) == 2 and len(s2) == 2:
                    # year in front
                    dfstr = "%Y/%m/%d"
                elif len(s2) == 4 and len(s1) == 2 and len(s0) == 2:
                    # year at end
                    dfstr = "%d/%m/%Y"
                elif len(s2) == 2 and len(s1) == 2 and len(s0) == 2:
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
                return ("10:00:00", "%H:%M:%S")
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

        if j.data.types.string.check(v):

            if v.strip() in ["0", ""]:
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
        js_shell 'j.data.types.date.test()'
        """
        c = """
        11/30 22:50
        11/30
        1990/11/30
        1990/11/30 10am:50
        1990/11/30 10pm:50
        1990/11/30 22:50
        30/11/1990
        30/11/1990 10pm:50
        """
        c = j.core.text.strip(c)
        out = ""
        for line in c.split("\n"):
            if line.strip() == "":
                continue
            epoch = self.clean(line)
            out += "%s -> %s\n" % (line, self.toString(epoch))
        out_compare = """
        11/30 22:50 -> 2018/11/30 22:50:00
        11/30 -> 2018/11/30 10:00:00
        1990/11/30 -> 1990/11/30 10:00:00
        1990/11/30 10am:50 -> 1990/11/30 10:50:00
        1990/11/30 10pm:50 -> 1990/11/30 22:50:00
        1990/11/30 22:50 -> 1990/11/30 22:50:00
        30/11/1990 -> 1990/11/30 10:00:00
        30/11/1990 10pm:50 -> 1990/11/30 22:50:00
        """
        print(out)
        out = j.core.text.strip(out)
        out_compare = j.core.text.strip(out_compare)
        assert out == out_compare
