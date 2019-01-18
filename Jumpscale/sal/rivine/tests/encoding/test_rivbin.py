
from Jumpscale.sal.rivine.encoding.rivbin import \
    encode, encode_slice, encode_array, encode_all, encode_currency, \
    encode_int, encode_int64, encode_int32, encode_int24, encode_int16, encode_int8, \
    IntegerOutOfRange, SliceLengthOutOfRange, \
    RivbinEncoder, \
    _encode_slice_length

import pytest

def test_encode_int24():
    """
    Test encoding 24 bits integer
    """
    hex_str = '7af905'
    int_value = int.from_bytes(bytearray.fromhex(hex_str), byteorder='little')
    result = encode_int24(int_value)
    assert hex_str == result.hex()
    result = encode_int(int_value)
    assert hex_str == result.hex()
    result = encode(int_value)
    assert hex_str == result.hex()

def test_encode_int_lower_bound_exception():
    with pytest.raises(IntegerOutOfRange):
        encode(-1)
    with pytest.raises(IntegerOutOfRange):
        encode_int(-1)
    with pytest.raises(IntegerOutOfRange):
        encode_int64(-1)
    with pytest.raises(IntegerOutOfRange):
        encode_int32(-1)
    with pytest.raises(IntegerOutOfRange):
        encode_int24(-1)
    with pytest.raises(IntegerOutOfRange):
        encode_int16(-1)
    with pytest.raises(IntegerOutOfRange):
        encode_int8(-1)

def test_encode_int_upper_bound_exception():
    with pytest.raises(IntegerOutOfRange):
        encode(1 << 64)
    with pytest.raises(IntegerOutOfRange):
        encode_int(1 << 64)
    with pytest.raises(IntegerOutOfRange):
        encode_int64(1 << 64)
    with pytest.raises(IntegerOutOfRange):
        encode_int32(1 << 32)
    with pytest.raises(IntegerOutOfRange):
        encode_int24(1 << 24)
    with pytest.raises(IntegerOutOfRange):
        encode_int16(1 << 16)
    with pytest.raises(IntegerOutOfRange):
        encode_int8(1 << 8)

def test_encode_slice_and_array():
    test_cases = [
        {
            'value': [],
            'expected_slice_result': bytearray(b'\x00'),
            'expected_array_result': bytearray(),
        },
        {
            'value': [False, True, False],
            'expected_slice_result': bytearray(b'\x06\x00\x01\x00'),
            'expected_array_result': bytearray(b'\x00\x01\x00'),
        },
    ]

    for tc in test_cases:
        result = encode_slice(tc['value'])
        assert tc['expected_slice_result'] == result
        result = encode_array(tc['value'])
        assert tc['expected_array_result'] == result

def test_encode_slice_iterator():
    result = encode(range(3))
    assert bytearray(b'\x06\x00\x01\x02') == result

def test_encode_slice_length():
    """
    Tests encoding the slice length
    """
    test_cases = [
        # one byte
        {
            'value': 0,
            'expected_result': 1
        },
        {
            'value': 1,
            'expected_result': 1
        },
        {
            'value': 42,
            'expected_result': 1
        },
        {
            'value': (1<<5),
            'expected_result': 1
        },
        {
            'value': (1<<6),
            'expected_result': 1
        },
        # two bytes
        {
            'value': (1<<7),
            'expected_result': 2
        },
        {
            'value': (1<<8),
            'expected_result': 2
        },
        {
            'value': 15999,
            'expected_result': 2
        },
        {
            'value': (1<<12),
            'expected_result': 2
        },
        {
            'value': (1<<14)-1,
            'expected_result': 2
        },
        # three bytes
        {
            'value': (1<<14),
            'expected_result': 3
        },
        {
            'value': (1<<15),
            'expected_result': 3
        },
        {
            'value': 2000000,
            'expected_result': 3
        },
        {
            'value': (1<<19),
            'expected_result': 3
        },
        {
            'value': (1<<21)-1,
            'expected_result': 3
        },
        # four bytes
        {
            'value': (1<<21),
            'expected_result': 4
        },
        {
            'value': (1<<22),
            'expected_result': 4
        },
        {
            'value': (1<<24),
            'expected_result': 4
        },
        {
            'value': (1<<25),
            'expected_result': 4
        },
        {
            'value': (1<<28)-1,
            'expected_result': 4
        },
        {
            'value': (1<<29)-1,
            'expected_result': 4
        },
    ]

    for tc in test_cases:
        result = len(_encode_slice_length(tc['value']))
        assert tc['expected_result'] == result

def test_encode_slice_length_exception():
    with pytest.raises(SliceLengthOutOfRange):
       _encode_slice_length(1<<29)

def test_rivbin_encoder():
    class Answer(RivbinEncoder):
        def __init__(self, number=0):
            self._number = number
        def rivbin_encode(self):
            if self._number%2 != 0:
                return encode_int24(self._number - 1)
            return encode_int24(self._number)
    
    test_cases = [
        {
            'value': Answer(),
            'expected_result': bytearray(b'\x00\x00\x00'),
        },
        {
            'value': Answer(42),
            'expected_result': bytearray(b'\x2A\x00\x00'),
        },
        {
            'value': Answer(43),
            'expected_result': bytearray(b'\x2A\x00\x00'),
        },
    ]

    for tc in test_cases:
        result = encode(tc['value'])
        assert tc['expected_result'] == result

def test_encode_all():
    test_cases = [
        {
            'values': [],
            'expected_result': bytearray(),
        },
        {
            'values': [False],
            'expected_result': bytearray(b'\x00'),
        },
        {
            'values': [42, True, "foo", [4, 2], range(1)],
            'expected_result': bytearray(b'\x2A\x01\x06foo\x04\x04\x02\x02\x00'),
        },
    ]

    for tc in test_cases:
        result = encode_all(*tc['values'])
        assert tc['expected_result'] == result

def test_encode_currency():
    test_cases = [
        {
            'value': 0,
            'expected_result': bytearray(b'\x00'),
        },
        {
            'value': 5577006791947779410,
            'expected_result': bytearray(b'\x10\x4d\x65\x82\x21\x07\xfc\xfd\x52'),
        },
        {
            'value': 35,
            'expected_result': bytearray(b'\x02\x23'),
        },
        {
            'value': 8674665223082153551,
            'expected_result': bytearray(b'\x10\x78\x62\x9a\x0f\x5f\x3f\x16\x4f'),
        },
        {
            'value': 1111111111111,
            'expected_result': bytearray(b'\x0c\x01\x02\xb3\x62\x11\xc7'),
        },
        {
            'value': 18446744073709551615,
            'expected_result': bytearray(b'\x10\xff\xff\xff\xff\xff\xff\xff\xff'),
        },
    ]

    for tc in test_cases:
        result = encode_currency(tc['value'])
        assert tc['expected_result'] == result

def test_encode_unknown_type():
    with pytest.raises(ValueError):
        encode(Exception('foo'))

def test_encode_bool():
    value = True
    output = encode(value)
    expected_output = bytearray(b'\x01')
    assert output == expected_output, "Failed to encode boolean value to binary"
