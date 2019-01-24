from Jumpscale import j

class IntegerOutOfRange(Exception):
    """
    IntegerOutOfRange error
    """

_INT_UPPERLIMIT = pow(2, 64) - 1

from abc import ABC, abstractmethod

class SiaBinaryObjectEncoderBase(ABC):
    @abstractmethod
    def sia_binary_encode(self, encoder):
        """
        sia_binary_encode encodes this object as a byte-slice,
        using the primitive encoding functions provided by the SiaBinaryEncoder module,
        resulting in a custom and/or complex byteslice,
        encoded according to the siabin encoding specification.
        """
        pass

class SiaBinaryEncoder(j.application.JSBaseClass):
    """
    Module implementing the siabin binary encoding,
    for the purposes of creating signatures only.

    Decoding of siabin-encoded data is not supported,
    and is out of scope for the siabin data encoding module.

    official specification can be found at
    https://github.com/threefoldtech/rivine/blob/18b19eac90f3cf9585a7ad4de4ecd612bee9c8e6/doc/encoding/SiaEncoding.md
    """

    def _init(self):
        self._data = bytearray()

    @property
    def data(self):
        return self._data

    def add_int(self, value):
        """
        Add an encoded integer as 8 bytes, using little-endianness,
        as specified by the siabin encoding specification.

        @param value: int value that fits in maximum 8 bytes
        """
        if not isinstance(value, int):
            raise TypeError("value is not an integer")
        if value < 0:
            raise IntegerOutOfRange("integer {} is out of lower range of 0".format(value))
        if value > _INT_UPPERLIMIT:
            raise IntegerOutOfRange("integer {} is out of upper range of {}".format(value, _INT_UPPERLIMIT))
        self._data += value.to_bytes(8, byteorder='little')

    def add_array(self, value):
        """
        Add an iterateble value as an array, encoding each element
        as specified by the siabin encoding specification.

        @param value: the iterateble object to be siabin-encoded as an array
        """
        if type(value) is str:
            self._data += value.encode('utf-8')
        elif type(value) in (bytes, bytearray):
            self._data += value
        else:
            try:
                result = bytearray()
                for element in value:
                    self.add(element)
                return result
            except TypeError:
                raise TypeError("value cannot be encoded as an array")

    def add_slice(self,value):
        """
        Add an encoded iterateble value as a slice,
        as specified by the siabin encoding specification.

        @param value: the iterateble object to be siabin-encoded as a slice
        """
        if type(value) is str:
            self.add_int(len(value))
            self._data += value.encode('utf-8')
        elif type(value) in (bytes, bytearray):
            self.add_int(len(value))
            self._data += value
        else:
            length = 0
            for _ in value:
                length += 1
            self.add_int(length)
            self.add_array(value)

    def add(self,value):
        """
        add a value as specified by the siabin encoding specification,
        automatically matching the value's type with a matching siabin type.

        Use a specific encoding function if you want to make sure you
        encode in a specific way.

        @param value: the value to be siabin-encoded
        """

        # if the value implements the SiabinEncoder interface,
        # we ignore the underlying type and use the custom-defined logic
        # as provided by the SiabinEncoder object
        if isinstance(value, SiaBinaryObjectEncoderBase):
            value.sia_binary_encode(encoder=self)
            return

        # try to siabin-encode the value based on its python type
        value_type = type(value)
        if value_type in (bytes, bytearray):
            self.add_slice(value)
        elif value_type is int:
            self.add_int(value)
        elif value_type is bool:
            self._data += bytearray([1]) if value else bytearray([0])
        else:
            # try to siabin-encode the value as a slice
            try:
                return self.add_slice(value)
            except TypeError:
                pass
            raise ValueError("cannot siabin-encode value with unsupported type {}".format(value_type))

    def add_all(self, *values):
        """
        Add values, one by one, and encode each as specified by the siabin encoding specification,
        automatically matching each value's type with a matching siabin type.

        Each value is encoded one after another within a single bytearray.

        @param values: the values to be siabin-encoded
        """
        for value in values:
            self.add(value)
