""" Definition of several primitive type properties (integer, string,...)
"""
from Jumpscale import j
import base64

class String():

    '''
    Generic string type
    stored in capnp as string
    '''

    NAME = 'string'
    BASETYPE = 'string'

    def fromString(self, s):
        """
        return string from a string (is basically no more than a check)
        """
        return self.clean(s)

    def toString(self, v):
        return self.clean(v)

    def toHR(self, v):
        return self.clean(v)

    def toJSON(self,v):
        return self.clean(v)

    def check(self, value):
        '''Check whether provided value is a string'''
        return isinstance(value, str)

    def get_default(self):
        return ""

    def clean(self, value):
        """
        will do a strip
        """
        if value is None:
            value = ""
        value = str(value)
        return value.strip()  # .strip("'").strip("\"").strip()

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        value = self.clean(value)
        return "'%s'" % value

    def toml_string_get(self, value, key=""):
        """
        will translate to what we need in toml
        """
        if key == "":
            return "'%s'" % (self.clean(value))
        else:
            return "%s = '%s'" % (key, self.clean(value))

    def capnp_schema_get(self, name, nr):
        return "%s @%s :Text;" % (name, nr)

    def unique_sort(self,txt):
        return "".join(j.data.types.list.clean(txt))


class StringMultiLine(String):

    NAME = 'stringmultiline'     # this really does not match with the
    BASETYPE = 'stringmultiline' # list of aliases.

    def check(self, value):
        '''Check whether provided value is a string and has \n inside'''
        return isinstance(value, str) and "\n" in value

    def clean(self, value):
        """
        will do a strip on multiline
        """
        value = str(value)
        return j.core.text.strip(value)

    def toString(self, v):
        v = self.clean(v)
        return v

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        value = self.clean(value)
        # value = value.replace("\n", "\\n")
        out0 = ""
        out0 += "'''\n"
        for item in value.split("\n"):
            out0 += "%s\n" % item
        out0 = out0.rstrip()
        out0 += "%s\n'''\n\n" % out0
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


class Bytes():
    '''
    Generic array of bytes type
    stored as bytes directly, no conversion
    '''

    NAME = 'bytes'
    BASETYPE = 'bytes'

    def fromString(self, s):
        """
        """
        if not isinstance(s, str):
            raise ValueError("Should be string:%s" % s)
        return s.encode()

    def toString(self, v):
        v = self.clean(v)
        return base64.b64encode(v).decode()

    def toHR(self, v):
        return "...BYTES..."

    def toJSON(self,v):
        return self.toString(v)

    def check(self, value):
        '''Check whether provided value is a array of bytes'''
        return isinstance(value, bytes)

    def get_default(self):
        return b""

    def clean(self, value):
        """
        only support b64encoded strings and binary strings
        """
        if isinstance(value,str):
            value = base64.b64decode(value)
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

    def toml_string_get(self, value, key):
        raise NotImplemented()


class Boolean():

    '''Generic boolean type'''

    NAME = 'boolean'
    BASETYPE = 'boolean'

    def fromString(self, s):
        return self.clean(s)

    # def checkString(self, s):
    #     """
    #     string which says True or true or false or False are considered to be textual representations
    #     """
    #     return s.lower().strip() == "true"

    def toString(self, boolean):
        if self.check(boolean):
            return str(boolean)
        else:
            raise ValueError("Invalid value for boolean: '%s'" % boolean)

    def toHR(self, v):
        return self.clean(v)

    def check(self, value):
        '''Check whether provided value is a boolean'''
        return value is True or value is False

    def get_default(self):
        return False

    def toJSON(self,v):
        return self.clean(v)

    def clean(self, value):
        """
        used to change the value to a predefined standard for this type
        """
        if value in ["1", 1, True]:
            value = True
        elif j.data.types.string.check(value) and value.strip().lower() in ["true", "yes", "y"]:
            value = True
        else:
            value = False
        return value

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


class Integer():

    '''Generic integer type'''

    NAME = 'integer'
    BASETYPE = 'integer'

    def checkString(self, s):
        return s.isdigit()

    def check(self, value):
        '''Check whether provided value is an integer'''
        return isinstance(value, int)

    def toString(self, value):
        if int(value) == 4294967295:
            return "-"  #means not set yet
        if self.check(value):
            return str(value)
        else:
            raise ValueError("Invalid value for integer: '%s'" % value)

    def toHR(self, v):
        if int(v) == 4294967295:
            return "-"  #means not set yet
        return self.clean(v)

    def fromString(self, s):
        return j.core.text.getInt(s)

    def get_default(self):
        #return this high number, is like None, not set yet
        return 4294967295

    def toJSON(self,v):
        return self.clean(v)

    def clean(self, value):
        """
        used to change the value to a predefined standard for this type
        """
        return int(value)

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


class Float():

    '''Generic float type'''

    NAME = 'float'
    BASETYPE = 'float'

    def checkString(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def check(self, value):
        '''Check whether provided value is a float'''
        return isinstance(value, float)

    def toString(self, value):
        if self.check(value):
            return str(value)
        else:
            raise ValueError("Invalid value for float: '%s'" % value)

    def toHR(self, v):
        return self.clean(v)

    def toJSON(self,v):
        return self.clean(v)

    def fromString(self, s):
        return j.core.text.getFloat(s)

    def get_default(self):
        return 0.0

    def clean(self, value):
        """
        used to change the value to a predefined standard for this type
        """
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


class Percent(Integer):

    '''
    stored as integer,
    to deal with percentages < 1 we multiply with 100 before storing

    as input support:

    xx%
    when int: is native format is multiples of 100 e.g. 1000 is 10%
    when string: is e.g. 99 which would be 99%
    when float is e.g. 0.5 which would be 50%

    '''

    NAME = 'percent'
    BASETYPE = 'integer'

    def clean(self, value):
        """
        used to change the value to a predefined standard for this type
        """
        if self.string.check(value):
            if "%" in value:
                return int(value.replace("%", "")) * 100
            else:
                return int(value) * 100
        elif self.integer.check(value):
            return value
        elif self.float.check(value):
            return value * 10000
        else:
            raise RuntimeError(
                "could not convert input to percent, input was:%s" %
                value)

    def fromString(self, s):
        s = self.clean(s)
        return s

    def toHR(self, v):
        return self.toString(v)

    def toString(self, v):
        v = self.clean(v)
        v = round(v / 100, 2)
        if int(v) == v:
            v = int(v)
        return "%s/%" % v


class Object(Bytes):
    '''
    is capnp object in binary format
    '''

    NAME = 'object'
    BASETYPE = 'bytes'

    def fromString(self, s):
        """
        """
        raise NotImplemented()

    def toString(self, v):
        return "BYTES"

    def check(self, value):
        return isinstance(value, bytes)

    def get_default(self):
        return b""

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


class JSObject(Bytes):
    '''
    jumpscale ORM object
    '''

    NAME = 'jsobject'
    BASETYPE = ''

    def __init__(self):
        self.SUBTYPE = None

    def fromString(self, s):
        """
        """
        return str(s)

    def toString(self, v):
        return v

    def check(self, value):
        return "_JSOBJ" in value.__dict__

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
