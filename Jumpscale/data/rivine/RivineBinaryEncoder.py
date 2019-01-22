"""
Module implementing the rivbin binary encoding,
for the purposes of creating signatures only.

Decoding of rivbin-encoded data is not supported,
and is out of scope for the rivine SAL
(the official python library implementation of Rivine Light).

https://github.com/threefoldtech/rivine/blob/7c87733e250d0e195c87119208fe7ba15e762e4b/doc/encoding/RivineEncoding.md
"""

from Jumpscale import j


##ERRORS
class IntegerOutOfRange(Exception):
    """
    IntegerOutOfRange error
    """


class SliceLengthOutOfRange(Exception):
    """
    SliceLengthOutOfRange error
    """

_INT_1BYTE_UPPERLIMIT = pow(2, 8) - 1
_INT_2BYTE_UPPERLIMIT = pow(2, 16) - 1
_INT_3BYTE_UPPERLIMIT = pow(2, 24) - 1
_INT_4BYTE_UPPERLIMIT = pow(2, 32) - 1
_INT_8BYTE_UPPERLIMIT = pow(2, 64) - 1

class RivineBinaryEncoder(j.application.JSBaseClass):
    """
    rivbin_encode encodes this object as a byte-slice,
    using the primitive encoding functions provided by the rivbin library,
    resulting in a custom and/or complex byteslice,
    encoded according to the rivbin encoding specification.
    """



    def _init(self):
        self.data = b""


    def add(self,value):
        """
        Encode a value as specified by the rivbin encoding specification,
        automatically matching the value's type with a matching rivbin type.

        Use a specific encoding function if you want to make sure you
        encode in a specific way.

        @param value: the value to be rivbin-encoded
        """

        # # if the value implements the RivbinEncoder interface,
        # # we ignore the underlying type and use the custom-defined logic
        # # as provided by the RivbinEncoder object
        # if isinstance(value, RivbinEncoder):
        #     result = value.rivbin_encode()
        #     if type(result) not in (bytes, bytearray):
        #         raise ValueError("expected rivbin-encoded value to be a bytearray, but instead was {}".format(type(value)))
        #     return result

        # try to rivbin-encode the value based on its python type
        value_type = type(value)
        if value_type in (bytes, bytearray):
            self.data += value
        elif value_type is int:
            self.add_int(value)
        elif value_type is bool:
            if value:
                self.data += bytearray([1])
            else:
                self.data += bytearray([0])
        else:
            # try to rivbin-encode the value as a slice
            try:
                self.add_slice(value)
            except TypeError:
                pass
            raise ValueError("cannot rivbin-encode value with unsupported type {}".format(value_type))

    # def add_int(self,value):
    #     """
    #     Encode an integer to the amount of bytes required, using little-endianness,
    #     as specified by the rivbin encoding specification.
    #
    #     Use the int-size specific encoding functions
    #     if you need the binary data to be encoded as a specific size,
    #     regardless of the limits of the passed value.
    #
    #     @param value: int value that fits in maximum 8 bytes
    #     """
    #     if not isinstance(value, int):
    #         raise TypeError("value is not an integer")
    #     if value <= _INT_1BYTE_UPPERLIMIT:
    #         return add_int8(value)
    #     if value <= _INT_2BYTE_UPPERLIMIT:
    #         return add_int16(value)
    #     if value <= _INT_3BYTE_UPPERLIMIT:
    #         return add_int24(value)
    #     if value <= _INT_4BYTE_UPPERLIMIT:
    #         return add_int32(value)
    #     return add_int64(value)

    def _check_int_type(self,value, limit):
        if not isinstance(value, int):
            raise TypeError("value is not an integer")
        if value < 0:
            raise IntegerOutOfRange("integer {} is out of lower range of 0".format(value))
        if value > limit:
            raise IntegerOutOfRange("integer {} is out of upper range of {}".format(value, limit))

    def add_int8(self,value):
        """
        Encode an uin8/int8 as a single byte, using little-endianness,
        as specified by the rivbin encoding specification.

        @param value: int value that fits in a single byte
        """
        self._check_int_type(value, _INT_1BYTE_UPPERLIMIT)
        self.data += value.to_bytes(1, byteorder='little')

    def add_int16(self,value):
        """
        Encode an uin16/int16 as two bytes, using little-endianness,
        as specified by the rivbin encoding specification.

        @param value: int value that fits in two bytes
        """
        self._check_int_type(value, _INT_2BYTE_UPPERLIMIT)
        self.data += value.to_bytes(2, byteorder='little')

    def add_int24(self,value):
        """
        Encode an uin24/int24 as three bytes, using little-endianness,
        as specified by the rivbin encoding specification.

        @param value: int value that fits in three bytes
        """
        self._check_int_type(value, _INT_3BYTE_UPPERLIMIT)
        self.data += value.to_bytes(3, byteorder='little')

    def add_int32(self,value):
        """
        Encode an uin32/int32 as four bytes, using little-endianness,
        as specified by the rivbin encoding specification.

        @param value: int value that fits in four bytes
        """
        self._check_int_type(value, _INT_4BYTE_UPPERLIMIT)
        self.data += value.to_bytes(4, byteorder='little')

    def add_int64(self,value):
        """
        Encode an uint64/int64 as three bytes, using little-endianness,
        as specified by the rivbin encoding specification.

        @param value: int value that fits in eight bytes
        """
        self._check_int_type(value, _INT_8BYTE_UPPERLIMIT)
        self.data += value.to_bytes(8, byteorder='little')

    def add_array(self,value):
        """
        Encode an iterateble value as an array,
        as specified by the rivbin encoding specification.

        @param value: the iterateble object to be rivbin-encoded as an array
        """
        if type(value) is str:
            return value.encode('utf-8')
        try:
            for element in value:
                self.data += self.encode(element)
        except TypeError:
            raise TypeError("value cannot be encoded as an array")


    def add_slice(self,value):
        """
        Encode an iterateble value as a slice,
        as specified by the rivbin encoding specification.

        @param value: the iterateble object to be rivbin-encoded as a slice
        """
        if type(value) is str:
            self._add_slice_length(len(value))
            self.data += value.encode('utf-8')
        else:
            value = [i for i in value]
            self._add_slice_length(len(value))
            self.add_array(value)

    def _add_slice_length(self,length):
        """
        Encodes the length of the slice
        """
        if length < pow(2, 7):
            self.add_int8(length << 1)
        if length < pow(2, 14):
            self.add_int16(1 | length << 2)
        if length < pow(2, 21):
            self.add_int24(3 | length << 3)
        if length < pow(2, 29):
            self.add_int32(7 | length << 3)
        raise SliceLengthOutOfRange("slice length {} is out of range".format(length))



    def add_all(self,*values):
        """
        Encode values, one by one, as specified by the rivbin encoding specification,
        automatically matching each value's type with a matching rivbin type.

        Each value is encoded one after another within a single bytearray.

        @param values: the values to be rivbin-encoded
        """
        for value in values:
            self.add(value)

    def add_currency(self,value):
        """
        Encode an integer as a currency value, using big-endianness,
        as specified by the rivbin encoding specification.

        Remark that this value is encoded using big-endianness
        as the only primitive defined by the rivbin spec.

        There is no size limit other than the limit defined by
        the rivbin slice encoding specification.

        @param value: int value that fits in four bytes
        """
        if type(value) is not int:
            raise ValueError("cannot rivbin-encode currency as it is not an integer")
        nbytes, rem = divmod(value.bit_length(), 8)
        self.add_slice(value.to_bytes(nbytes+int(bool(rem)), byteorder='big'))

