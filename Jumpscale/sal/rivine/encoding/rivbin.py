"""
Module implementing the rivbin binary encoding,
for the purposes of creating signatures only.
Decoding of rivbin-encoded data is now supported.

https://github.com/threefoldtech/rivine/blob/7c87733e250d0e195c87119208fe7ba15e762e4b/doc/encoding/RivineEncoding.md
"""

from abc import ABC, abstractmethod

class RivbinEncoder(ABC):
    @abstractmethod
    def rivbin_encode(self):
        """
        rivbin_encode encodes this object as a byte-slice,
        using the primitive encoding functions provided by the rivbin library,
        resulting in a custom and/or complex byteslice,
        encoded according to the rivbin encoding specification.
        """
        pass

class IntegerOutOfRange(Exception):
    """
    IntegerOutOfRange error
    """

_INT_1BYTE_UPPERLIMIT = pow(2, 8) - 1
_INT_2BYTE_UPPERLIMIT = pow(2, 16) - 1
_INT_3BYTE_UPPERLIMIT = pow(2, 24) - 1
_INT_4BYTE_UPPERLIMIT = pow(2, 32) - 1
_INT_8BYTE_UPPERLIMIT = pow(2, 64) - 1

def encode_int(value):
    """
    Encode an integer to the amount of bytes required, using little-endianness,
    as specified by the rivbin encoding specification.

    Use the int-size specific encoding functions
    if you need the binary data to be encoded as a specific size,
    regardless of the limits of the passed value.

    @param value: int value that fits in maximum 8 bytes
    """
    if not isinstance(value, int):
        raise TypeError("value is not an integer")
    if value <= _INT_1BYTE_UPPERLIMIT:
        return encode_int8(value)
    if value <= _INT_2BYTE_UPPERLIMIT:
        return encode_int16(value)
    if value <= _INT_3BYTE_UPPERLIMIT:
        return encode_int24(value)
    if value <= _INT_4BYTE_UPPERLIMIT:
        return encode_int32(value)
    return encode_int64(value)

def _check_int_type(value, limit):
    if not isinstance(value, int):
        raise TypeError("value is not an integer")
    if value < 0:
        raise IntegerOutOfRange("integer {} is out of lower range of 0".format(value))
    if value > limit:
        raise IntegerOutOfRange("integer {} is out of upper range of {}".format(value, limit))

def encode_int8(value):
    """
    Encode an uin8/int8 as a single byte, using little-endianness,
    as specified by the rivbin encoding specification.

    @param value: int value that fits in a single byte
    """
    _check_int_type(value, _INT_1BYTE_UPPERLIMIT)
    return value.to_bytes(1, byteorder='little')

def encode_int16(value):
    """
    Encode an uin16/int16 as two bytes, using little-endianness,
    as specified by the rivbin encoding specification.

    @param value: int value that fits in two bytes
    """
    _check_int_type(value, _INT_2BYTE_UPPERLIMIT)
    return value.to_bytes(2, byteorder='little')

def encode_int24(value):
    """
    Encode an uin24/int24 as three bytes, using little-endianness,
    as specified by the rivbin encoding specification.

    @param value: int value that fits in three bytes
    """
    _check_int_type(value, _INT_3BYTE_UPPERLIMIT)
    return value.to_bytes(3, byteorder='little')

def encode_int32(value):
    """
    Encode an uin32/int32 as four bytes, using little-endianness,
    as specified by the rivbin encoding specification.

    @param value: int value that fits in four bytes
    """
    _check_int_type(value, _INT_4BYTE_UPPERLIMIT)
    return value.to_bytes(4, byteorder='little')

def encode_int64(value):
    """
    Encode an uint64/int64 as three bytes, using little-endianness,
    as specified by the rivbin encoding specification.

    @param value: int value that fits in eight bytes
    """
    _check_int_type(value, _INT_8BYTE_UPPERLIMIT)
    return value.to_bytes(8, byteorder='little')

def encode_array(value):
    """
    Encode an iterateble value as an array,
    as specified by the rivbin encoding specification.

    @param value: the iterateble object to be rivbin-encoded as an array
    """
    if type(value) is str:
        return value.encode('utf-8')
    try:
        result = bytearray()
        for element in value:
            result.extend(encode(element))
        return result
    except TypeError:
        raise TypeError("value cannot be encoded as an array")

class SliceLengthOutOfRange(Exception):
    """
    SliceLengthOutOfRange error
    """

def encode_slice(value):
    """
    Encode an iterateble value as a slice,
    as specified by the rivbin encoding specification.

    @param value: the iterateble object to be rivbin-encoded as a slice
    """
    if type(value) is str:
        result = bytearray(_encode_slice_length(len(value)))
        result.extend(value.encode('utf-8'))
        return result
    try:
        elements = bytearray()
        length = 0
        for element in value:
            elements.extend(encode(element))
            length += 1
        result = bytearray(_encode_slice_length(length))
        result.extend(elements)
        return result
    except TypeError:
        pass
    raise TypeError("value cannot be encoded as a slice")

def _encode_slice_length(length):
    """
    Encodes the length of the slice
    """
    if length < pow(2, 7):
        return encode_int8(length << 1)
    if length < pow(2, 14):
        return encode_int16(1 | length << 2)
    if length < pow(2, 21):
        return encode_int24(3 | length << 3)
    if length < pow(2, 29):
        return encode_int32(7 | length << 3)
    raise SliceLengthOutOfRange("slice length {} is out of range".format(length))

def encode(value):
    """
    Encode a value as specified by the rivbin encoding specification,
    automatically matching the value's type with a matching rivbin type.

    Use a specific encoding function if you want to make sure you
    encode in a specific way.

    @param value: the value to be rivbin-encoded
    """

    # if the value implements the RivbinEncoder interface,
    # we ignore the underlying type and use the custom-defined logic
    # as provided by the RivbinEncoder object
    if isinstance(value, RivbinEncoder):
        result = value.rivbin_encode()
        if type(result) not in (bytes, bytearray):
            raise ValueError("expected rivbin-encoded value to be a bytearray, but instead was {}".format(type(value)))
        return result

    # try to rivbin-encode the value based on its python type
    value_type = type(value)
    if value_type in (bytes, bytearray):
        result = bytearray()
        result.extend(value)
        return result
    elif value_type is int:
        return encode_int(value)
    elif value_type is bool:
        return bytearray([1]) if value else bytearray([0])

    # try to rivbin-encode the value as a slice
    try:
        return encode_slice(value)
    except TypeError:
        pass
    raise ValueError("cannot rivbin-encode value with unsupported type {}".format(value_type))

def encode_all(*values):
    """
    Encode values, one by one, as specified by the rivbin encoding specification,
    automatically matching each value's type with a matching rivbin type.

    Each value is encoded one after another within a single bytearray.

    @param values: the values to be rivbin-encoded
    """
    result = bytearray()
    for value in values:
        result.extend(encode(value))
    return result

def encode_currency(value):
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
    return encode_slice(value.to_bytes(nbytes+int(bool(rem)), byteorder='big'))
