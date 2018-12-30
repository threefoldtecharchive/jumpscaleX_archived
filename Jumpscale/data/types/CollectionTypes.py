'''Definition of several collection types (list, dict, set,...)'''

from Jumpscale import j


from Jumpscale.data.types.PrimitiveTypes import (String, StringMultiLine, Bytes,
                             Boolean, Integer,
                             Float, Percent, Object, JSObject)

import struct


class YAML(String):
    '''Generic dictionary type'''

    NAME = 'yaml'
    BASETYPE = 'dictionary'

    def check(self, value):
        '''Check whether provided value is a dict'''
        return isinstance(value, dict)

    def get_default(self):
        return dict()

    def fromString(self, s):
        """
        return string from a dict
        """
        if j.data.types.dict.check(s):
            return s
        else:
            # s = s.replace("''", '"')
            j.data.serializers.yaml.loads(s)
            return s

    def toString(self, v):
        return j.data.serializers.yaml.dumps(v)


class JSON(String):

    NAME = 'json'
    BASETYPE = 'dictionary'


class Dictionary():
    '''Generic dictionary type'''

    NAME = 'dictionary'
    BASETYPE = 'dictionary'

    def check(self, value):
        '''Check whether provided value is a dict'''
        return isinstance(value, dict)

    def get_default(self):
        return dict()
        # if self._default is NO_DEFAULT:
        #     return dict()
        # return dict(self._default)

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

    def toString(self, v):
        return j.data.serializers.json.dumps(v, True, True)

    def toJSON(self, v):
        return self.toString(v)

    def capnp_schema_get(self, name, nr):
        raise RuntimeError("not implemented")

    def python_code_get(self, value, sort=False):
        """
        produce the python code which represents this value
        """
        return str(value)


class List():
    '''Generic list type'''
    NAME = 'list'
    BASETYPE = 'list'

    def __init__(self):
        self.SUBTYPE = None

    def check(self, value):
        '''Check whether provided value is a list'''
        return isinstance(value, (list, tuple))
        # self.list_check_1type(value)

    def get_default(self):
        return list()

    def list_check_1type(self, llist, die=True):
        if len(llist) == 0:
            return True
        ttype = j.data.types.type_detect(llist[0])
        for item in llist:
            res = ttype.check(item)
            if not res:
                if die:
                    raise RuntimeError("List is not of 1 type.")
                else:
                    return False
        return True

    def fromString(self, v, ttype=None):
        if ttype is None:
            ttype = self.SUBTYPE
        if v is None:
            v = ""
        if ttype is not None:
            ttype = ttype.NAME
        v = j.core.text.getList(v, ttype)
        v = self.clean(v)
        if self.check(v):
            return v
        else:
            raise ValueError("List not properly formatted.")

    def clean(self, val, toml=False, sort=False, unique=True, ttype=None):
        if ttype is None:
            ttype = self.SUBTYPE
        else:
            if j.data.types.string.check(val):
                val = [i.strip() for i in val.split(",")]
        if len(val) == 0:
            return val
        if ttype is None:
            self.SUBTYPE = j.data.types.type_detect(val[0])
            ttype = self.SUBTYPE
        res = []
        if j.data.types.string.check(val):
            val = [i.strip() for i in val.split(",")]
        for item in val:
            if not toml:
                item = ttype.clean(item)
            else:
                item = ttype.toml_string_get(item)
            if unique:
                if item not in res:
                    res.append(item)
            else:
                res.append(item)
        if sort:
            res.sort()
        return res

    def toString(self, val, clean=True, sort=False):
        """
        will translate to what we need in toml
        """
        if clean:
            val = self.clean(val, toml=False, sort=sort)
        if len(str(val)) > 30:
            # multiline
            out = ""
            for item in val:
                out += "%s,\n" % item
            out += "\n"
        else:
            out = ""
            for item in val:
                out += " %s," % item
            out = out.strip().strip(",").strip()
        return out



    def python_code_get(self, value, sort=False):
        """
        produce the python code which represents this value
        """
        value = self.clean(value, toml=False, sort=sort)
        out = "[ "
        for item in value:
            out += "%s, " % self.SUBTYPE.python_code_get(item)
        out = out.strip(",")
        out += " ]"
        return out

    def toml_string_get(self, val, key="", clean=True, sort=True):
        """
        will translate to what we need in toml
        """
        if clean:
            val = self.clean(val, toml=True, sort=sort)
        if key == "":
            raise NotImplemented()
        else:
            out = ""
            if len(str(val)) > 30:
                # multiline
                out += "%s = [\n" % key
                for item in val:
                    out += "    %s,\n" % item
                out += "]\n\n"
            else:
                out += "%s = [" % key
                for item in val:
                    out += " %s," % item
                out = out.rstrip(",")
                out += " ]\n"
        return out

    def toml_value_get(self, val, key=""):
        """
        will from toml string to value
        """
        if key == "":
            raise NotImplemented()
        else:
            return j.data.serializers.toml.loads(val)

    def capnp_schema_get(self, name, nr):
        s = self.SUBTYPE.capnp_schema_get("name", 0)
        if self.SUBTYPE.BASETYPE in ["string", "integer", "float", "bool"]:
            capnptype = self.SUBTYPE.capnp_schema_get("", 0).split(":", 1)[
                1].rstrip(";").strip()
        else:
            # the sub type is now bytes because that is how the subobjects will
            # be stored
            capnptype = j.data.types.bytes.capnp_schema_get(
                "", nr=0).split(":", 1)[1].rstrip(";").strip()
        return "%s @%s :List(%s);" % (name, nr, capnptype)


class Hash(List):

    '''hash is 2 value list, represented as 2 times 4 bytes'''

    NAME = 'hash'
    BASETYPE = 'string'

    def fromString(self, s):
        """
        return string from a string (is basically no more than a check)
        """
        if not isinstance(s, str):
            raise ValueError("Should be string:%s" % s)
        s = self.clean(s)
        return s

    def toString(self, value):
        v0, v1 = self.clean(value)
        return "%s:%s" % (v0, v1)

    def check(self, value):
        return isinstance(value, (list, tuple)) and len(value) == 2

    def get_default(self):
        return (0, 0)

    def clean(self, value):
        """
        will do a strip
        """

        def bytesToInt(val):
            if j.data.types.bytes.check(val):
                if len(val) is not 4:
                    raise RuntimeError(
                        "byte for first part of hash can only be 4 bytes")
                return struct.unpack("I", val)
            else:
                return int(val)

        if j.data.types.list.check(value) or j.data.types.set.check(value):
            # prob given as list or set of 2 which is the base representation
            if len(value) != 2:
                raise RuntimeError("hash can only be list/set of 2")
            v0 = bytesToInt(value[0])
            v1 = bytesToInt(value[1])
            return (v0, v1)

        elif j.data.types.bytes.check(value):
            if len(value) is not 8:
                raise RuntimeError("bytes should be len 8")
            #means is byte
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


class Set(List):
    '''Generic set type'''

    NAME = 'set'
    BASETYPE = 'set'

    def check(self, value):
        '''Check whether provided value is a set'''
        return isinstance(value, set)

    def get_default(self):
        return list()
