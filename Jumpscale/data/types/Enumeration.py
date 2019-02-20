from .PrimitiveTypes import String
from .TypeBaseClasses import TypeBaseClass
from Jumpscale import j


class EnumerationObj(TypeBaseClass):

    '''
    Generic string type
    stored in capnp as int
    '''
    NAME = 'enum'
    BASETYPE = 'string'
    ALIAS = "e"
    __slots__ = ['values', 'default', "_md5", "_jumpscale_location" ]

    def __init__(self, values):

        if isinstance(values, str):
            values = values.split(",")
            values = [item.strip().strip("'").strip().strip('"').strip() for item in values]
        if not isinstance(values, list):
            raise RuntimeError("input for enum is comma separated str or list")
        self.values = [item.upper().strip() for item in values]
        self.default = self.values[0]
        self.values.sort()
        self._md5 = j.data.hash.md5_string(str(self))  # so it has the default as well
        j.data.types.enumerations[self._md5] = self
        self._jumpscale_location = "j.data.types.enumerations['%s']" % self._md5

    def capnp_schema_get(self, name, nr):
        return "%s @%s :UInt32;" % (name, nr)


    def toData(self,val):
        val = self.clean(val)
        return self.values.index(val)+1

    def get_default(self):
        return self.values[0]

    def clean(self, value):
        """
        can use int or string,
        will find it and return as string
        """
        try:
            value = int(value)
        except:
            pass
        if isinstance(value, str):
            value = value.upper().strip()
            if value not in self.values:
                raise RuntimeError("could not find enum:'%s' in '%s'" % (value, self.__repr__()))
            return value
        elif isinstance(value, int):
            if value == 0:
                raise RuntimeError("could not find enum id:%s in '%s', should not be 0" % (value, self.__repr__()))
            if value > len(self.values)+1:
                raise RuntimeError("could not find enum id:%s in '%s', too high" % (value, self.__repr__()))
            return self.values[value-1]
        else:
            raise RuntimeError("unsupported type for enum, is int or string")

    def __str__(self):
        return "ENNUM: %s (default:%s)" % (self.__repr__(), self.default)

    def __repr__(self):
        return ",".join(self.values)


class Enumeration(TypeBaseClass):

    '''
    Generic string type
    stored in capnp as int
    '''

    NAME = 'enum'
    BASETYPE = 'int'
    ALIAS = "e"


    def get(self, values):
        """
        :param ttype:
        :param kwargs: e.g. values="red,blue,green" can also a list for e.g. enum
        :return:

        e.g. for enumeration

        """
        return EnumerationObj(values)

