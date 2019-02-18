""" Definition of several primitive type properties (integer, string,...)
"""
from Jumpscale import j
import base64
from .TypeBaseClasses import *


class String(TypeBaseClass):

    '''
    Generic string type
    stored in capnp as string
    '''

    NAME = 'string'
    ALIAS = "str,s"
    BASETYPE = 'string'

    def fromString(self, s):
        """
        return string from a string (is basically no more than a check)
        """
        return self.clean(s)

    def toJSON(self, v):
        return self.clean(v)

    def check(self, value):
        '''Check whether provided value is a string'''
        return isinstance(value, str)

    def clean(self, value):
        """
        will do a strip
        """
        if value is None:
            value = ""
        try:
            value = str(value)
        except Exception as e:
            raise j.exceptions.input("cannot convert to string")

        value = value.strip().strip("'").strip().strip("\"").strip()

        return value

    def unique_sort(self, txt):
        return "".join(j.data.types.list.clean(txt))


class StringMultiLine(String):

    NAME = 'multiline'     # this really does not match with the
    BASETYPE = 'stringmultiline'  # list of aliases.
    ALIAS = "multiline"

    def check(self, value):
        '''Check whether provided value is a string and has \n inside'''
        return isinstance(value, str) and ("\\n" in value or "\n" in value)

    def clean(self, value):
        """
        will do a strip on multiline
        """
        if value is None:
            value = ""
        try:
            value = str(value)
        except Exception as e:
            raise j.exceptions.input("cannot convert to string")
        return value

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        value = self.clean(value)
        out0 = ""
        out0 += "'''\n"
        for item in value.split("\n"):
            out0 += "%s\n" % item
        out0 = out0.rstrip()
        out0 += "\n'''"
        if out0 == "''''''":
            out0 = "'''default \n value '''"
        return out0

    def toml_string_get(self, value, key=""):
        """
        will translate to what we need in toml
        """
        if key == "":
            out = self.python_code_get(value)
        else:
            value = self.clean(value)
            out0 = ""
            # multiline
            out0 += "%s = '''\n" % key
            for item in value.split("\n"):
                out0 += "    %s\n" % item
            out0 = out0.rstrip()
            out = "%s\n    '''" % out0
        return out


class Bytes(TypeBaseClass):
    '''
    Generic array of bytes type
    stored as bytes directly, no conversion
    '''

    NAME = 'bytes'
    BASETYPE = 'bytes'
    ALIAS = "bin"

    def fromString(self, s):
        """
        """
        if isinstance(str,s):
            try:
                s=base64.b64decode(s) #could be rather dangerous
                return s
            except:
                pass
            s = j.data.types.string.clean(s)
            return s.encode()
        else:
            raise j.exceptions.input("input is not string")

    def toString(self, v):
        v = self.clean(v)
        return base64.b64encode(v).decode()

    def toHR(self, v):
        return self.toString(v)

    def toJSON(self, v):
        return self.toString(v)

    def check(self, value):
        '''Check whether provided value is a array of bytes'''
        return isinstance(value, bytes)

    def get_default(self):
        return b""

    def clean(self, value):
        """
        supports b64encoded strings, std strings which can be encoded and binary strings
        """
        if isinstance(value, str):
            value = self.fromString(value)
        else:
            if not self.check(value):
                raise RuntimeError("byte input required")
        return value

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        return self.clean(value)

    def capnp_schema_get(self, name, nr):
        return "%s @%s :Data;" % (name, nr)

    def toml_string_get(self, value, key=""):
        if key == "":
            return self.toString(value)
        else:
            out = "%s = %s" % (key, self.toString(value))
            return out


class Boolean(TypeBaseClass):

    '''Generic boolean type'''

    NAME = 'boolean'
    BASETYPE = 'boolean'
    ALIAS = "b,bool"

    def fromString(self, s):
        return self.clean(s)

    def toHR(self, v):
        return self.clean(v)

    def check(self, value):
        '''Check whether provided value is a boolean'''
        return value is True or value is False

    def get_default(self):
        return False

    def toJSON(self, v):
        return self.clean(v)

    def clean(self, value):
        """
        if string and true, yes, y, 1 then True
        if int and 1 then True

        everything else = False

        """
        if isinstance(value, str):
            value = j.data.types.string.clean(value).lower().strip()
            return value in ["true", "yes", "y","1"]
        return value in [1, True]

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        value = self.clean(value)
        if value:
            value = "True"
        else:
            value = "False"
        return value

    def toml_string_get(self, value, key=""):
        value = self.clean(value)
        if key == "":
            if value:
                value = "true"
            else:
                value = "false"
            return value
        else:

            if value:
                out = "%s = true" % (key)
            else:
                out = "%s = false" % (key)

            return out

    def capnp_schema_get(self, name, nr):
        return "%s @%s :Bool;" % (name, nr)


class Integer(TypeBaseClass):

    '''Generic integer type'''

    NAME = 'integer'
    ALIAS = 'int,i'
    BASETYPE = 'integer'

    def checkString(self, s):
        return s.isdigit()

    def check(self, value):
        '''Check whether provided value is an integer'''
        return isinstance(value, int)

    def toHR(self, v):
        if int(v) == 4294967295:
            return "-"  # means not set yet
        return '{:,}'.format(self.clean(v))

    def fromString(self, s):
        return self.clean(s)

    def get_default(self):
        # return this high number, is like None, not set yet
        return 4294967295

    def toJSON(self, v):
        return self.clean(v)

    def clean(self, value):
        """
        used to change the value to a predefined standard for this type
        """
        if isinstance(value, float):
            value = int(value)
        elif isinstance(value, str):
            value = j.data.types.string.clean(value).strip()
            if "," in value:
                value = value.replace(",", "")
            value = int(value)
        if not self.check(value):
            raise ValueError("Invalid value for integer: '%s'" % value)
        return value

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        return self.toml_string_get(value)

    def toml_string_get(self, value, key=""):
        """
        will translate to what we need in toml
        """
        if key == "":
            return "%s" % (self.clean(value))
        else:
            return "%s = %s" % (key, self.clean(value))

    def capnp_schema_get(self, name, nr):
        return "%s @%s :UInt32;" % (name, nr)


class Float(TypeBaseClass):

    '''Generic float type'''

    NAME = 'float'
    BASETYPE = 'float'
    ALIAS = "f,float"

    def checkString(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def check(self, value):
        '''Check whether provided value is a float'''
        return isinstance(value, float)

    def toHR(self, v):
        return "%d" % v

    def toJSON(self, v):
        return self.clean(v)

    def fromString(self, s):
        s = self.clean(s)
        return j.core.text.getFloat(s)

    def get_default(self):
        return 0.0

    def clean(self, value):
        """
        """
        if self.check(value):
            return value
        return float(value)

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        return self.toml_string_get(value)

    def toml_string_get(self, value, key=""):
        """
        will translate to what we need in toml
        """
        if key == "":
            return "%s" % (self.clean(value))
        else:
            return "%s = %s" % (key, self.clean(value))

    def capnp_schema_get(self, name, nr):
        return "%s @%s :Float64;" % (name, nr)


class Percent(Float):

    '''
    stored as float, 0-1
    can input as string xx%
    when int: is native format is 0-1 in float
    when float is e.g. 0.5 which would be 0.5% #be carefull


    '''

    NAME = 'percent'
    ALIAS = 'perc,p'
    BASETYPE = 'float'

    def clean(self, value):
        """
        used to change the value to a predefined standard for this type
        """
        if isinstance(value, str):
            value = value.strip().strip("\"").strip("'").strip()
            if "%" in value:
                value = value.replace("%", "")
                value = float(value)/100
            else:
                value = float(value)
        elif isinstance(value, int) or isinstance(value, float):
            value = float(value)
        else:
            raise RuntimeError("could not convert input to percent, input was:%s" % value)

        assert value < 1.00001
        return value

    def get_default(self):
        return 0.0

    def toHR(self, v):
        return "{:.2%}".format(self.clean(v))

    def toString(self, v):
        v = self.clean(v)
        if int(v) == v:
            v = int(v)
        return "{}%".format(v)


class CapnpBin(Bytes):
    '''
    #TODO
    is capnp object in binary format
    '''

    NAME = 'capnpbin'
    BASETYPE = 'bytes'
    ALIAS = "cbin"

    def clean(self, value):
        """
        """
        return value

    def toHR(self, v):
        return self.clean(v)

    def python_code_get(self, value):
        raise NotImplemented()

    def capnp_schema_get(self, name, nr):
        return "%s @%s :Data;" % (name, nr)

    def toml_string_get(self, value, key):
        raise NotImplemented()


class JSDataObject(Bytes):
    '''
    jumpscale data object as result of using j.data.schemas.
    '''

    NAME = 'jsobject'
    BASETYPE = ''
    ALIAS = "o,obj"

    def __init__(self):
        self.SUBTYPE = None

    def fromString(self, s):
        """
        """
        return str(s)

    def toString(self, v):
        return v

    def check(self, value):
        try:
            return "_JSOBJ" in value.__dict__
        except:
            return False

    def get_default(self):
        return self.SUBTYPE()

    def clean(self, value):
        """
        """
        return value

    def toHR(self, v):
        return str(v)

    def python_code_get(self, value):
        return "None"

    def capnp_schema_get(self, name, nr):
        return "%s @%s :Data;" % (name, nr)

    def toml_string_get(self, value, key):
        raise NotImplemented()


class JSConfigObject(TypeBaseClass):
    '''
    jumpscale object which inherits from j.application.JSBaseConfigClass
    '''

    NAME = 'jsconfigobject'
    BASETYPE = ''
    ALIAS = "configobj"

    def check(self, value):
        return isinstance(value, j.application.JSBaseConfigClass)
