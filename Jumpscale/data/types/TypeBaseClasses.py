
from Jumpscale import j


class TypeBaseObjClass():

    def __init__(self,typebase,value=None):
        __slots__ = ['_typebase', '_value']

        self._typebase = typebase
        if value is None:
            self._data = None
        else:
            self._data = self._typebase.toData(value) #returns the native lowest level type

    def _capnp_schema_get(self, name, nr):
        return self._typebase.capnp_schema_get(name,nr)

    @property
    def _string(self):
        raise j.exceptions.NotImplemented()

    @property
    def _python_code(self):
        raise j.exceptions.NotImplemented()

    @property
    def value(self):
        raise j.exceptions.NotImplemented()

    @value.setter
    def value(self,val):
        self._data = self._typebase.toData(val)

    def __str__(self):
        if self._data:
            return "%s: %s"%(self._typebase.__class__.NAME, self._string)
        else:
            return "%s: NOTSET"%(self._typebase.__class__.NAME)

    __repr__ = __str__


class TypeBaseObjClassNumeric(TypeBaseObjClass):

    @property
    def value(self):
        raise j.exceptions.NotImplemented()


    # def __hash__(self):
    #     return hash(self.value)

    def __eq__(self, other):
        other = self._other_convert(other)
        if other is None:
            return None
        return float(other) == float(self)

    def __bool__(self):
        return self._data is not None

    def _other_convert(self,other):
        try:
            return self._typebase.clean(other)
        except:
            pass

    def __add__(self, other):
        other = self._other_convert(other)
        return self._typebase.clean(float(other) + float(self))

    def __iadd__(self, other):
        other = self._other_convert(other)
        self.value = float(self) + float(other)
        return self

    def __sub__(self, other):
        other = self._other_convert(other)
        return self._typebase.clean(float(self) - float(other))

    def __mul__(self, other):
        other = self._other_convert(other)
        return self._typebase.clean(float(self) * float(other))

    def __matmul__(self, other):
        other = self._other_convert(other)
        return self._typebase.clean(float(self) @ float(other))

    def __truediv__(self, other):
        other = self._other_convert(other)
        return self._typebase.clean(float(self) / float(other))

    def __floordiv__(self, other):
        other = self._other_convert(other)
        return self._typebase.clean(float(self) // float(other))

    def __mod__(self, other):
        raise NotImplemented()

    def __divmod__(self, other):
        raise NotImplemented()

    def __pow__(self, other):
        raise NotImplemented()

    def __lshift__(self):
        raise NotImplemented()

    def __neg__(self):
        return self._typebase.clean(float(self) * -1)

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)


    __rshift__ = __lshift__
    __and__ = __lshift__
    __xor__ = __lshift__
    __or__ = __lshift__

class TypeBaseClass():

    def toString(self, v):
        return str(self.clean(v))

    def toHR(self, v):
        return self.toString(v)

    def toData(self, v):
        return self.clean(v)

    def check(self, value):
        '''
        - if there is a specific implementation e.g. string, float, enumeration, it will check if the input is that implementation
        - if not strict implementation or we cannot know e.g. an address will return None
        '''
        raise RuntimeError("not implemented")

    def possible(self, value):
        """
        will check if it can be converted to the jumpscale representation, basically the clean works without error
        :return:
        """
        try:
            self.clean(str(value))
            return True
        except Exception as e:
            return False

    def get_default(self):
        return ""

    def clean(self, value):
        """
        """
        raise RuntimeError("not implemented")


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


class TypeBaseObjClassFactory(TypeBaseClass):

    def get_default(self):
        return self.clean("0")

    def capnp_schema_get(self, name, nr):
        """
        is 5 bytes, 1 for type, 4 for float value
        - j.clients.currencylayer.cur2id
        - j.clients.currencylayer.id2cur

        struct.pack("B",1)+struct.pack("f",1234234234.0)

        """
        return "%s @%s :Data;" % (name, nr)

    def check(self, value):
        if isinstance(value,TypeBaseObjClass):
            return True

    def fromString(self, txt):
        return self.clean(txt)

    def toJSON(self, v):
        return self.toString(v)

    def toString(self, val):
        val = self.clean(val)
        return val._string

    def python_code_get(self, value):
        """
        produce the python code which represents this value
        """
        val = self.clean(value)
        return val._python_code

    def toData(self, v):
        raise j.exceptions.NotImplemented()

    def clean(self, v):
        raise j.exceptions.NotImplemented()