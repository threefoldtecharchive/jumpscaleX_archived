'''Definition of several collection types (list, dict, set,...)'''

from Jumpscale import j

from Jumpscale.data.types.PrimitiveTypes import String, StringMultiLine
from Jumpscale.data.types.TypeBaseClasses import TypeBaseClass

import struct
from .TypeBaseClasses import *


class YAML(StringMultiLine):
    '''Generic dictionary type'''

    NAME =  'yaml'

    def __init__(self,default=None):

        self.BASETYPE = 'string'
        self.NOCHECK = True
        if not default:
            default = {}
        self._default = default


    def possible(self, value):
        '''Check whether provided value is a dict'''
        if not isinstance(value, str):
            return False
        try:
            j.data.serializers.yaml.loads(value)
        except ValueError:
            return False
        return True

    def clean(self, value):
        if value is None:
            value = self._default_get()
        elif not self.check(value):
            raise ValueError("Invalid value for yaml: %s" % value)
        value = j.data.types.string.clean(value)
        return value

    def fromString(self, s):
        """
        return string from a dict
        """
        if j.data.types.yaml.check(s):
            return s
        else:
            j.data.serializers.yaml.loads(s)
            return s

    def toString(self, v):
        return j.data.serializers.yaml.dumps(v)


class JSON(StringMultiLine):

    NAME =  'json'

    def __init__(self,default=None):
        self.BASETYPE = 'string'
        self.NOCHECK = True
        if not default:
            default = {}
        self._default = default

    def possible(self, value):
        """
        Check whether provided value is a dict
        """
        if not isinstance(value, str):
            return False
        try:
            j.data.serializers.json.loads(value)
        except ValueError:
            return False
        return True

    def clean(self, v=""):
        if value is None:
            return self._default_get()
        if not self.check(v):
            raise RuntimeError("Valid serialized json string is required")
        return v

    def fromString(self, v):
        return self.clean(v)

    def toJSON(self, v):
        return self.clean(v)

    def toHR(self, v):
        return self.toString(v)


class Dictionary(TypeBaseClass):
    '''Generic dictionary type'''

    NAME =  'dict'

    def __init__(self, default=None):

        self.BASETYPE = 'dict'
        if not default:
            default = {}
        self._default = default

    def check(self, value):
        '''Check whether provided value is a dict'''
        return isinstance(value, dict)

    def fromString(self, s):
        """
        return string from a dict
        """
        if j.data.types.dict.check(s):
            return s
        else:
            s = s.replace("''", '"')
            j.data.serializers.json.loads(s)
            return s

    def clean(self, v=""):
        """
        supports binary, string & dict
        if binary will use msgpack
        if string will use json
        :param v:
        :return:
        """
        if v is None:
            return self._default_get()
        if j.data.types.bytes.check(v):
            if v==b'':
                v={}
            else:
                v = j.data.serializers.msgpack.loads(v)
        elif j.data.types.string.check(v):
            v = j.data.serializers.json.loads(v)
        if not self.check(v):
            raise RuntimeError("dict for clean needs to be bytes, string or dict")
        return v

    def toString(self, v):
        v = self.clean(v)
        return j.data.serializers.json.dumps(v, True, True)

    def toJSON(self, v):
        return self.toString(v)

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        return self.toString(value)

    def toHR(self, v):
        return self.toString(v)

    def capnp_schema_get(self, name, nr):
        return "%s @%s :Data;" % (name, nr)


class Hash(TypeBaseClass):

    '''
    hash is 2 value list, represented as 2 times 4 bytes
    '''
    NAME =  'hash,h'
    CUSTOM = False

    def __init__(self,default=None):
        self.BASETYPE = 'string'
        if not default:
            default = (0,0)
        self._default = default

    def fromString(self, s):
        """
        return string from a string (is basically no more than a check)
        """
        if not isinstance(s, str):
            raise ValueError("Should be string:%s" % s)
        s = self.clean(s)
        return s

    def toString(self, value):
        """
        serialization to intnr:intnr
        :param value:
        :return:
        """
        v0, v1 = self.clean(value)
        return "%s:%s" % (v0, v1)

    def check(self, value):
        return isinstance(value, (list, tuple)) and len(value) == 2

    def clean(self, value):
        """
        will do a strip
        """
        if value is None:
            return self._default_get()
        def bytesToInt(val):
            if j.data.types.bytes.check(val):
                if len(val) is not 4:
                    raise RuntimeError("hash parts can only be 4 bytes")
                return struct.unpack("I", val)
            else:
                return int(val)

        if j.data.types.list.check(value):  # or j.data.types.set.check(value):
            # prob given as list or set of 2 which is the base representation
            if len(value) != 2:
                raise RuntimeError("hash can only be list/set of 2")
            v0 = bytesToInt(value[0])
            v1 = bytesToInt(value[1])
            return (v0, v1)

        elif j.data.types.bytes.check(value):
            if len(value) is not 8:
                raise RuntimeError("bytes should be len 8")
            # means is byte
            return struct.unpack("II", b"aaaadddd")

        elif j.data.types.string.check(value):
            if ":" not in value:
                raise RuntimeError(
                    "when string, needs to have : inside %s" %
                    value)
            v0, v1 = value.split(":")
            v0 = int(v0)
            v1 = int(v1)
            return (v0, v1)

        else:
            raise RuntimeError("unrecognized format for hash:%s" % value)

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        return "'%s'" % self.toString(value)

    def toml_string_get(self, value, key=""):
        """
        will translate to what we need in toml
        """
        if key == "":
            return self.python_code_get(value)
        else:
            return "%s = %s" % (key, self.python_code_get(value))

    def capnp_schema_get(self, name, nr):
        return "%s @%s :Data;" % (name, nr)

# TODO: why do we have a set, from our perspective a set & list should be same for novice users

# class Set(List):
#     '''Generic set type'''
#
#     self.NAME =  'set'
#     BASETYPE = 'set'
#
#     def check(self, value):
#         '''Check whether provided value is a set'''
#         if value == {}:
#             value = {"default"}
#
#         return isinstance(value, set)
#
#     def default_get(self):
#         return set()
#
#     def clean(self, value):
#         if not self.check(value):
#             raise ValueError("Valid set is required")
#         return value
#
#     def python_code_get(self, value, sort=False):
#         """
#         produce the python code which represents this value
#         """
#         value = self.clean(value)
#         out = "{ "
#         for item in value:
#             out += "%s, " % self.SUBTYPE.python_code_get(item)
#         out = out.strip(",")
#         out += " }"
#         return out
