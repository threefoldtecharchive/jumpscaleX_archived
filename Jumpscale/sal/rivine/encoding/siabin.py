"""
Module implementing the siabin binary encoding,
for the purposes of creating signatures only.

Decoding of siabin-encoded data is not supported,
and is out of scope for the rivine SAL
(the official python library implementation of Rivine Light).

https://github.com/threefoldtech/rivine/blob/18b19eac90f3cf9585a7ad4de4ecd612bee9c8e6/doc/encoding/SiaEncoding.md
"""

from abc import ABC, abstractmethod

class SiabinEncoder(ABC):
    @abstractmethod
    def siabin_encode(self):
        """
        siabin_encode encodes this object as a byte-slice,
        using the primitive encoding functions provided by the siabin library,
        resulting in a custom and/or complex byteslice,
        encoded according to the siabin encoding specification.
        """
        pass

class IntegerOutOfRange(Exception):
    """
    IntegerOutOfRange error
    """

_INT_UPPERLIMIT = pow(2, 64) - 1

def encode_int(value):
    """
    Encode an integer as 8 bytes, using little-endianness,
    as specified by the siabin encoding specification.

    @param value: int value that fits in maximum 8 bytes
    """
    if not isinstance(value, int):
        raise TypeError("value is not an integer")
    if value < 0:
        raise IntegerOutOfRange("integer {} is out of lower range of 0".format(value))
    if value > _INT_UPPERLIMIT:
        raise IntegerOutOfRange("integer {} is out of upper range of {}".format(value, _INT_UPPERLIMIT))
    return value.to_bytes(8, byteorder='little')

def encode_array(value):
    """
    Encode an iterateble value as an array,
    as specified by the siabin encoding specification.

    @param value: the iterateble object to be siabin-encoded as an array
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

def encode_slice(value):
    """
    Encode an iterateble value as a slice,
    as specified by the siabin encoding specification.

    @param value: the iterateble object to be siabin-encoded as a slice
    """
    if type(value) is str:
        result = bytearray(encode_int(len(value)))
        result.extend(value.encode('utf-8'))
        return result
    try:
        elements = bytearray()
        length = 0
        for element in value:
            elements.extend(encode(element))
            length += 1
        result = bytearray(encode_int(length))
        result.extend(elements)
        return result
    except TypeError:
        pass
    raise TypeError("value cannot be encoded as a slice")

def encode_currency(value):
    """
    Encode an integer as a currency value, using big-endianness,
    as specified by the siabin encoding specification.

    Remark that this value is encoded using big-endianness
    as the only primitive defined by the siabin spec.
    
    There is no size limit other than the limit defined by
    the siabin slice encoding specification.

    @param value: int value that fits in four bytes
    """
    if type(value) is not int:
        raise ValueError("cannot siabin-encode currency as it is not an integer")
    if value < 0:
        raise ValueError("negative currency values are not allowed in siabin-encoding")
    nbytes, rem = divmod(value.bit_length(), 8)
    if rem:
        nbytes += 1
    return encode_all(nbytes, value.to_bytes(nbytes, byteorder='big'))

def encode(value):
    """
    Encode a value as specified by the siabin encoding specification,
    automatically matching the value's type with a matching siabin type.

    Use a specific encoding function if you want to make sure you
    encode in a specific way.

    @param value: the value to be siabin-encoded
    """

    # if the value implements the SiabinEncoder interface,
    # we ignore the underlying type and use the custom-defined logic
    # as provided by the SiabinEncoder object
    if isinstance(value, SiabinEncoder):
        result = value.siabin_encode()
        if type(result) not in (bytes, bytearray):
            raise ValueError("expected siabin-encoded value to be a bytearray, but instead was {}".format(type(value)))
        return result

    # try to siabin-encode the value based on its python type
    value_type = type(value)
    if value_type in (bytes, bytearray):
        result = bytearray()
        result.extend(value)
        return result
    elif value_type is int:
        return encode_int(value)
    elif value_type is bool:
        return bytearray([1]) if value else bytearray([0])

    # try to siabin-encode the value as a slice
    try:
        return encode_slice(value)
    except TypeError:
        pass
    raise ValueError("cannot siabin-encode value with unsupported type {}".format(value_type))

def encode_all(*values):
    """
    Encode values, one by one, as specified by the siabin encoding specification,
    automatically matching each value's type with a matching siabin type.

    Each value is encoded one after another within a single bytearray.

    @param values: the values to be siabin-encoded
    """
    result = bytearray()
    for value in values:
        result.extend(encode(value))
    return result
