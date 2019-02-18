
from Jumpscale import j


class TypeBaseObjClass():

    def __init__(self,typebase,value):
        __slots__ = ['_typebase', '_value']

        self._typebase = typebase
        self._value_ = self._typebase.clean(value)

    def _capnp_schema_get(self, name, nr):
        return self._typebase.capnp_schema_get(name,nr)

    @property
    def _string(self):
        return self._typebase._toString(self._value_)

    @property
    def _data(self):
        return self._typebase._toData(self._value_)

    @property
    def _python_code(self):
        return self._typebase._python_code_get(self._value_)

    @property
    def _value(self):
        return self._value_

    @_value.setter
    def _value(self,val):
        self._value_ = self._typebase.clean(val)

    def __str__(self):
        if self._value_:
            return "%s: %s"%(self._typebase.__class__.NAME,self._value)
        else:
            return "%s: NOTSET"%(self._typebase.__class__.NAME)

    __repr__ = __str__


class TypeBaseObjClassNumeric(TypeBaseObjClass):

    @property
    def _value(self):
        return float(self._value_)

    @_value.setter
    def _value(self,val):
        self._value_ = self._typebase.clean(val)


    # def __hash__(self):
    #     return hash(self._value)

    def __eq__(self, other):
        other = self._other_convert(other)
        return other == float(self._value)

    def __bool__(self):
        return self._value is not None

    def _other_convert(self,other):
        if isinstance(other,TypeBaseObjClass):
            return float(self._typebase.clean(other._value))
        else:
            return float(self._typebase.clean(other))

    def __add__(self, other):
        other = self._other_convert(other)
        return other + float(self._value)

    def __iadd__(self, other):
        other = self._other_convert(other)
        self.value = other + float(self._value)
        return self

    def __sub__(self, other):
        other = self._other_convert(other)
        return float(self._value)- other

    def __mul__(self, other):
        other = self._other_convert(other)
        return float(self._value)* other

    def __matmul__(self, other):
        other = self._other_convert(other)
        return float(self._value)@ other

    def __truediv__(self, other):
        other = self._other_convert(other)
        return float(self._value)/ other

    def __floordiv__(self, other):
        other = self._other_convert(other)
        return float(self._value)// other

    def __mod__(self, other):
        raise NotImplemented()

    def __divmod__(self, other):
        raise NotImplemented()

    def __pow__(self, other):
        raise NotImplemented()

    def __lshift__(self):
        raise NotImplemented()

    def __neg__(self):
        return float(self._value)* -1

    def __float__(self):
        return float(self._value)

    def __int__(self):
        return int(self._value)


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
        raise RuntimeError("not implemented")
        # return "%s @%s :Text;" % (name, nr)

