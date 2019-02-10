from .PrimitiveTypes import String
from .TypeBaseClasses import TypeBaseObjClass

class EnumerationObj(TypeBaseObjClass):

    '''
    Generic string type
    stored in capnp as string
    '''


    def __init__(self, values):

        if isinstance(values, str):
            values = values.split(",")
            values = [item.strip().strip("'").strip().strip('"').strip() for item in values]
        if not isinstance(values, list):
            raise RuntimeError("input for enum is comma separated str or list")
        self.values = [item.upper().strip() for item in values]
        self.default = self.values[0]
        self.values.sort()
        self.values_str = ",".join(self.values)
        self._md5 = j.data.hash.md5_string(str(self))  # so it has the default as well
        self._jumpscale_location = "j.data.types.enumerations['%s']" % self._md5

    def check(self, value):
        '''Check whether provided value is a string'''
        try:
            self.clean()
        except:
            return False
        return True

    def capnp_schema_get(self, name, nr):
        return "%s @%s :UInt32;" % (name, nr)

    def get_default(self):
        return self.default

    def toString(self, v):
        return self.clean(v)

    def toData(self, v):
        v = self.clean(v)
        return self.values.index(v)+1

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
                raise RuntimeError("could not find enum:'%s' in '%s'" % (value, self.values_str))
            return value
        elif isinstance(value, int):
            if value == 0:
                raise RuntimeError("could not find enum id:%s in '%s', tshould not be 0" % (value, self.values_str))
            if value > len(self.values)+1:
                raise RuntimeError("could not find enum id:%s in '%s', too high" % (value, self.values_str))
            return self.values[value-1]
        else:
            raise RuntimeError("unsupported type for enum, is int or string")

    def __str__(self):
        return "ENNUM: %s (default:%s)" % (self.values_str, self.default)

    __repr__ = __str__



class Enumeration(String):

    '''
    Generic string type
    stored in capnp as string
    '''

    NAME = 'enum'
    BASETYPE = 'string'
    ALIAS = "e"

    def get(self, values=[]):

        if isinstance(values, str):
            values = values.split(",")
            values = [item.strip().strip("'").strip().strip('"').strip() for item in values]
        if not isinstance(values, list):
            raise RuntimeError("input for enum is comma separated str or list")
        self.values = [item.upper().strip() for item in values]
        self.default = self.values[0]
        self.values.sort()
        self.values_str = ",".join(self.values)
        self._md5 = j.data.hash.md5_string(str(self))  # so it has the default as well
        self._jumpscale_location = "j.data.types.enumerations['%s']" % self._md5

    def check(self, value):
        '''Check whether provided value is a string'''
        try:
            self.clean()
        except:
            return False
        return True

    def capnp_schema_get(self, name, nr):
        return "%s @%s :UInt32;" % (name, nr)

    def get_default(self):
        return self.default

    def toString(self, v):
        return self.clean(v)

    def toData(self, v):
        v = self.clean(v)
        return self.values.index(v)+1

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
                raise RuntimeError("could not find enum:'%s' in '%s'" % (value, self.values_str))
            return value
        elif isinstance(value, int):
            if value == 0:
                raise RuntimeError("could not find enum id:%s in '%s', tshould not be 0" % (value, self.values_str))
            if value > len(self.values)+1:
                raise RuntimeError("could not find enum id:%s in '%s', too high" % (value, self.values_str))
            return self.values[value-1]
        else:
            raise RuntimeError("unsupported type for enum, is int or string")

    def __str__(self):
        return "ENNUM: %s (default:%s)" % (self.values_str, self.default)

    __repr__ = __str__


