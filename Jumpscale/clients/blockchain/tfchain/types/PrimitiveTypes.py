from Jumpscale import j

from .BaseDataType import BaseDataTypeClass

from abc import abstractmethod

# TODO:
# Binary data should be one class with following options:
#   * Fixed-size or not (important for binary encoding) (1)
#   * format for str encoding (hex or base64) (2)
# We achieve (2) currently by using sub-classes, but (1) we support manually in the classes
# that own such binary data.
#
# ^ From this perspective is a hash just a fixed-size binary data
#   (in which case we do want to specify the size for validation)

class BaseBinaryData(BaseDataTypeClass):
    """
    BinaryData is the data type used for any binary data that is not a hash,
    for example: signatures
    """

    def __init__(self, value=None):
        self._value = None
        self.value = value

    @classmethod
    def from_json(cls, obj):
        if not isinstance(obj, str):
            raise TypeError("binary data is expected to be an encoded string when part of a JSON object")
        return cls(value=obj)

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if isinstance(value, BaseBinaryData):
            self._value = value.value
            return
        if not value:
            value = bytearray()
        elif isinstance(value, str):
            value = self.from_str(value)
        elif isinstance(value, bytes):
            value = bytearray(value)
        elif not isinstance(value, bytearray):
            raise TypeError("binary data can only be set to a str, bytes or bytearray, not {}".format(type(value)))
        self._value = value
    
    def __str__(self):
        return self.to_str(self._value)
    
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

    @abstractmethod
    def from_str(self, s):
        pass
    @abstractmethod
    def to_str(self, value):
        pass


class BinaryData(BaseBinaryData):
    def from_str(self, s):
        return bytearray.fromhex(s)
    def to_str(self, value):
        return value.hex()
    
class RawData(BaseBinaryData):
    def from_str(self, s):
        return bytearray(j.data.serializers.base64.decode(s))
    def to_str(self, value):
        return j.data.serializers.base64.dumps(self.value)


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
            elif not isinstance(value, bytearray):
                raise TypeError("hash can only be set to a str, bytes or bytearray, not {}".format(type(value)))
        if len(value) != Hash._SIZE:
            raise TypeError('hash has to have a fixed length of {}'.format(Hash._SIZE))
        self._value = value
    
    def __str__(self):
        return self._value.hex()
    
    __repr__ = __str__
    
    json = __str__

    def __eq__(self, other):
        other = Hash._op_other_as_hash(other)
        return self.value == other.value
    def __ne__(self, other):
        other = Hash._op_other_as_hash(other)
        return self.value != other.value

    def __hash__(self):
        return hash(str(self))

    @staticmethod
    def _op_other_as_hash(other):
        if isinstance(other, (str, bytes)):
            other = Hash(value=other)
        elif not isinstance(other, Hash):
            raise TypeError("Hash of type {} is not supported".format(type(other)))
        return other

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
        if not isinstance(obj, str):
            raise TypeError("currency is expected to be a string when part of a JSON object, not type {}".format(type(obj)))
        return cls(value=obj)
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if value is None:
            self._value = 0
            return
        if isinstance(value, Currency):
            self._value = value.value
            return
        if isinstance(value, str):
            value = self._parse_str(value)
        elif not isinstance(value, int):
            # float values are not allowed as our precision is high enough that
            # rounding errors can occur
            raise TypeError('currency can only be set to a str or int value, not type {}'.format(type(value)))
        else:
            value = int(value)
        if value < 0:
            raise TypeError('currency cannot have a negative value')
        self._value = value

    def _parse_str(self, value):
        """
        Parse a Currency str, either as a TFT value (with unit and/or with decimal notation),
        or as a string-encoded unit value.
        """
        value = value.upper().strip()
        if len(value) >= 4 and value[-3:] == 'TFT':
            value = value[:-3].rstrip()
            if '.' not in value:
                value += '.'
        if '.' in value:
            whole, integral = value.split(sep='.', maxsplit=1)
            lintegral = len(integral)
            if lintegral > 9:
                raise ValueError("Currency can only have a precision of maximum 9 decimals, not {}".format(lintegral))
            if lintegral < 9:
                integral += '0'*(9-lintegral)
            return int(whole+integral)
        return int(value)

    # operator overloading to allow currencies to be summed
    def __add__(self, other):
        other = Currency._op_other_as_currency(other)
        value = self.value + other.value
        return Currency(value=value)
    __radd__ = __add__
    def __iadd__(self, other):
        other = Currency._op_other_as_currency(other)
        self.value += other.value
        return self

    # operator overloading to allow currencies to be subtracted
    def __sub__(self, other):
        other = Currency._op_other_as_currency(other)
        value = self.value - other.value
        return Currency(value=value)
    __rsub__ = __sub__
    def __isub__(self, other):
        other = Currency._op_other_as_currency(other)
        self.value -= other.value
        return self

    # operator overloading to allow currencies to be compared
    def __lt__(self, other):
        other = Currency._op_other_as_currency(other)
        return self.value < other.value
    def __le__(self, other):
        other = Currency._op_other_as_currency(other)
        return self.value <= other.value
    def __eq__(self, other):
        other = Currency._op_other_as_currency(other)
        return self.value == other.value
    def __ne__(self, other):
        other = Currency._op_other_as_currency(other)
        return self.value != other.value
    def __gt__(self, other):
        other = Currency._op_other_as_currency(other)
        return self.value > other.value
    def __ge__(self, other):
        other = Currency._op_other_as_currency(other)
        return self.value >= other.value

    @staticmethod
    def _op_other_as_currency(other):
        if isinstance(other, (int, str)):
            other = Currency(value=other)
        elif not isinstance(other, Currency):
            raise TypeError("currency of type {} is not supported".format(type(other)))
        return other

    # allow our currency to be turned into an int
    def __int__(self):
        return self.value

    def __str__(self):
        return str(self._value)

    def totft(self, with_unit=False):
        """
        Turn this Currency value into a str TFT unit-based value,
        optionally with the currency notation.
        """
        s = str(self)
        l = len(s)
        if l > 9:
            s = s[:l-9] + '.' + s[-9:]
        else:
            s = '0.' + '0'*(9-l) + s
        s = s.rstrip('0')
        if s[-1] == '.':
            s = s[:-1]
        if with_unit:
            return s + ' TFT'
        return s
    
    def __repr__(self):
        return self.totft(with_unit=True)
    
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


class Blockstake(BaseDataTypeClass):
    """
    TFChain Blockstake Object.
    """
    def __init__(self, value=0):
        self._value = 0
        self.value = value

    @classmethod
    def from_json(cls, obj):
        if not isinstance(obj, str):
            raise TypeError("block stake is expected to be a string when part of a JSON object, not type {}".format(type(obj)))
        return cls(value=obj)
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        if value is None:
            self._value = 0
            return
        if isinstance(value, Currency):
            self._value = value.value
            return
        if isinstance(value, str):
            value = int(value)
        elif not isinstance(value, int):
            # float values are not allowed as our precision is high enough that
            # rounding errors can occur
            raise TypeError('block stake can only be set to a str or int value, not type {}'.format(type(value)))
        else:
            value = int(value)
        if value < 0:
            raise TypeError('block stake cannot have a negative value')
        self._value = value

    # allow our block stake to be turned into an int
    def __int__(self):
        return self.value
    
    def __str__(self):
        return str(self._value)
    __repr__ = __str__
    json = __str__

    def sia_binary_encode(self, encoder):
        """
        Encode this block stake (==Currency) according to the Sia Binary Encoding format.
        """
        nbytes, rem = divmod(self._value.bit_length(), 8)
        if rem:
            nbytes += 1
        encoder.add_int(nbytes)
        encoder.add_array(self._value.to_bytes(nbytes, byteorder='big'))
    
    def rivine_binary_encode(self, encoder):
        """
        Encode this block stake (==Currency) according to the Rivine Binary Encoding format.
        """
        nbytes, rem = divmod(self._value.bit_length(), 8)
        if rem:
            nbytes += 1
        encoder.add_slice(self._value.to_bytes(nbytes, byteorder='big'))
