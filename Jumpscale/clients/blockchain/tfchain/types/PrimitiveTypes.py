from Jumpscale import j

from .BaseDataType import BaseDataTypeClass

class BinaryData(BaseDataTypeClass):
    """
    BinaryData is the data type used for any binary data that is not a hash,
    for example: signatures and arbitrary data
    """

    def __init__(self, value=None):
        self._value = None
        if value == None:
            value = bytearray()
        self.value = value

    @classmethod
    def from_json(cls, obj):
        if type(obj) is not str:
            raise TypeError("binary data is expected to be a hex-encoded string when part of a JSON object")
        return cls(value=obj)
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        vt = type(value)
        if vt is None:
            value = bytearray()
        elif vt is str:
            value = bytearray.fromhex(value)
        elif vt is bytes:
            value = bytearray(value)
        elif vt is not bytearray:
            raise TypeError("hash can only be set to a str, bytes or bytearray")
        self._value = value
    
    def __str__(self):
        return self._value.hex()
    
    __repr__ = __str__
    
    json = __str__

    def sia_binary_encode(self, encoder):
        """
        Encode this binary data according to the Sia Binary Encoding format.
        """
        encoder.add_slice(self._value)
    
    def rivine_binary_encode(self, encoder):
        """
        Encode this binary data according to the Rivine Binary Encoding format.
        """
        encoder.add_slice(self._value)


class Hash(BaseDataTypeClass):
    # hash size
    _SIZE = 32

    """
    TFChain Hash Object.
    """
    def __init__(self, value=None):
        self._value = None
        self.value = value

    @classmethod
    def from_json(cls, obj):
        if not isinstance(obj, str):
            raise TypeError("hash is expected to be a string when part of a JSON object")
        return cls(value=obj)
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if isinstance(value, Hash):
            self._value = value.value
            return
        if not value:
            value = bytearray(b'\x00'*Hash._SIZE)
        else:
            if isinstance(value, str):
                value = bytearray.fromhex(value)
            elif isinstance(value, bytes):
                value = bytearray(value)
            elif isinstance(value, bytearray):
                raise TypeError("hash can only be set to a str, bytes or bytearray")
        if len(value) != Hash._SIZE:
            raise TypeError('hash has to have a fixed length of {}'.format(Hash._SIZE))
        self._value = value
    
    def __str__(self):
        return self._value.hex()
    
    __repr__ = __str__
    
    json = __str__

    def sia_binary_encode(self, encoder):
        """
        Encode this hash according to the Sia Binary Encoding format.
        """
        encoder.add_array(self._value)
    
    def rivine_binary_encode(self, encoder):
        """
        Encode this hash according to the Rivine Binary Encoding format.
        """
        encoder.add_array(self._value)

from math import floor

class Currency(BaseDataTypeClass):
    """
    TFChain Currency Object.
    """
    def __init__(self, value=0):
        self._value = 0
        self.value = value

    @classmethod
    def from_json(cls, obj):
        if isinstance(obj, str):
            raise TypeError("currency is expected to be a string when part of a JSON object")
        return cls(value=obj)
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if isinstance(value, Currency):
            self._value = value.value
            return
        if isinstance(value, str):
            value = int(value)
        elif not isinstance(value, int):
            # float values are not allowed as our precision is high enough that
            # rounding errors can occur
            raise TypeError('currency can only be set to a str or int value')
        else:
            value = int(value)
        if value < 0:
            raise TypeError('currency cannot have a negative value')
        self._value = value
    
    def __str__(self):
        return str(self._value)
    
    def __repr__(self):
        return self.__str__() + ' TFT' # TODO, make more human readable
    
    json = __str__

    def sia_binary_encode(self, encoder):
        """
        Encode this currency according to the Sia Binary Encoding format.
        """
        nbytes, rem = divmod(self._value.bit_length(), 8)
        if rem:
            nbytes += 1
        encoder.add_int(nbytes)
        encoder.add_array(self._value.to_bytes(nbytes, byteorder='big'))
    
    def rivine_binary_encode(self, encoder):
        """
        Encode this currency according to the Rivine Binary Encoding format.
        """
        nbytes, rem = divmod(self._value.bit_length(), 8)
        if rem:
            nbytes += 1
        encoder.add_slice(self._value.to_bytes(nbytes, byteorder='big'))
