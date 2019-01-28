"""
Module to support binary encoding for tfchain
"""

SLICE_LENGTH_1BYTES_UPPERLIMIT = pow(2, 7)
SLICE_LENGTH_2BYTES_UPPERLIMIT = pow(2, 14)
SLICE_LENGTH_3BYTES_UPPERLIMIT = pow(2, 21)
SLICE_LENGTH_4BYTES_UPPERLIMIT = pow(2, 29)

UINT_1BYTE_UPPERLIMIT = pow(2, 8) - 1
UINT_2BYTE_UPPERLIMIT = pow(2, 16) - 1
UINT_3BYTE_UPPERLIMIT = pow(2, 24) - 1
UINT_4BYTE_UPPERLIMIT = pow(2, 32) - 1
UINT_8BYTE_UPPERLIMIT = pow(2, 64) - 1

class BinaryEncoder:
    """
    Support binary encoding for tfchain
    """
    @staticmethod
    def encode(value, type_=None):
        """
        Enocdes a value to its binary representation

        @param value: Value to be encoded
        @param type_: Type of the value, if not given, the type will be detected automatically
        """
        result = bytearray()
        if value is None:
            return result
        if type_ == 'slice':
            # slice is a variable size array, which means we need to prefix the size of the array and then we can encode the list itself
            result = SliceBinaryEncoder.encode(value)
        elif type_ == 'currency':
            nbytes, rem = divmod(value.bit_length(), 8)
            if rem:
                nbytes += 1
            result.extend(BinaryEncoder.encode(nbytes))
            result.extend(value.to_bytes(nbytes, byteorder='big'))
        elif type_ == 'hex':
            result.extend(bytearray.fromhex(value))
        elif type_ is None:
            # try to figure out the type of the value
            value_type = type(value)
            if value_type in (bytes, bytearray):
                result.extend(value)
            elif value_type is int:
                result = IntegerBinaryEncoder.encode(value)
            elif value_type is bool:
                result = bytearray([1]) if value else bytearray([0])
            elif value_type in (list, set, tuple, frozenset):
                for item in value:
                    result.extend(BinaryEncoder.encode(item))
            elif value_type is str:
                result = SliceBinaryEncoder.encode(value)
            elif hasattr(value, 'binary'):
                    result.extend(value.binary)
            else:
                raise ValueError('Cannot binary encode value with unknown type')
        else:
            raise ValueError('Cannot binary encode value with unknown type')
        return result

class SliceLengthOutOfRange(Exception):
    """
    SliceLengthOutOfRange error
    """

class SliceBinaryEncoder:
    """
    Support binary encoding for slice type
    Slice is an array with no pre-defined size
    """

    @staticmethod
    def encode_length(length):
        """
        Encodes the length of the slice
        """
        if length < SLICE_LENGTH_1BYTES_UPPERLIMIT:
            return IntegerBinaryEncoder.encode(length << 1)
        if length < SLICE_LENGTH_2BYTES_UPPERLIMIT:
            return IntegerBinaryEncoder.encode(1 | length << 2)
        if length < SLICE_LENGTH_3BYTES_UPPERLIMIT:
            return IntegerBinaryEncoder.encode(3 | length << 3)
        if length < SLICE_LENGTH_4BYTES_UPPERLIMIT:
            return IntegerBinaryEncoder.encode(7 | length << 3)
        raise SliceLengthOutOfRange("slice length {} is out of range".format(length))

    @staticmethod
    def encode(value):
        """
        Encodes a slice to a binary

        @param value: Value to be encoded
        """
        length = len(value)
        result = bytearray()
        result.extend(SliceBinaryEncoder.encode_length(length))
        if type(value) is str:
            result.extend(value.encode('utf-8'))
        else:
            # encode the content of the slice
            for item in value:
                result.extend(BinaryEncoder.encode(item))
        return result

class IntegerOutOfRange(Exception):
    """
    IntegerOutOfRange error
    """

class IntegerBinaryEncoder:
    """
    Support binary encoding for integers
    """
    @staticmethod
    def encode(value, _kind=None):
        """
        Encodes an integer value to binary

        @param value: Value to be encoded
        @param _kind: specific kind of integer (optional)
        """
        if value < 0:
            raise IntegerOutOfRange("integer {} is out of lower range".format(value))

        # encode forcing a specific kind of integer
        if _kind:
            return IntegerBinaryEncoder._encode_kind(value, _kind)

        # determine the size of the integer
        if value <= UINT_1BYTE_UPPERLIMIT:
            return value.to_bytes(1, byteorder='little')
        if value <= UINT_2BYTE_UPPERLIMIT:
            return value.to_bytes(2, byteorder='little')
        if value <= UINT_3BYTE_UPPERLIMIT:
            return value.to_bytes(3, byteorder='little')
        if value <= UINT_4BYTE_UPPERLIMIT:
            return value.to_bytes(4, byteorder='little')
        raise IntegerOutOfRange("integer {} is out of upper range".format(value))

    @staticmethod
    def _encode_kind(value, kind):
        if kind in ('uint8', 'int8'):
            if value > UINT_1BYTE_UPPERLIMIT:
                 raise IntegerOutOfRange("uint8/int8 {} is out of upper range".format(value))
            return value.to_bytes(1, byteorder='little')
        if kind in ('uint16', 'int16'):
            if value > UINT_2BYTE_UPPERLIMIT:
                 raise IntegerOutOfRange("uint16/int16 {} is out of upper range".format(value))
            return value.to_bytes(2, byteorder='little')
        if kind == 'uint24':
            if value > UINT_3BYTE_UPPERLIMIT:
                 raise IntegerOutOfRange("uint24 {} is out of upper range".format(value))
            return value.to_bytes(3, byteorder='little')
        if kind in ('uint32', 'int32'):
            if value > UINT_4BYTE_UPPERLIMIT:
                 raise IntegerOutOfRange("uint32/int32 {} is out of upper range".format(value))
            return value.to_bytes(4, byteorder='little')
        if kind in ('int', 'uint', 'uint64', 'int64'):
            if value > UINT_8BYTE_UPPERLIMIT:
                 raise IntegerOutOfRange("int/uint/uint64/int64 {} is out of upper range".format(value))
            return value.to_bytes(8, byteorder='little')
        raise ValueError('cannot encode unknown integer kind {}'.format(kind))
