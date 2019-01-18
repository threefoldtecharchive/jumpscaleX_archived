
from Jumpscale.sal.rivine.encoding.siabin import \
    encode, encode_slice, encode_array, encode_all, encode_currency, \
    encode_int, IntegerOutOfRange, SiabinEncoder

import pytest


def test_encode_int_lower_bound_exception():
    with pytest.raises(IntegerOutOfRange):
        encode(-1)
    with pytest.raises(IntegerOutOfRange):
        encode_int(-1)

def test_encode_int_upper_bound_exception():
    with pytest.raises(IntegerOutOfRange):
        encode(1 << 64)
    with pytest.raises(IntegerOutOfRange):
        encode_int(1 << 64)

def test_encode_slice_and_array():
    test_cases = [
        {
            'value': [],
            'expected_slice_result': bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'),
            'expected_array_result': bytearray(),
        },
        {
            'value': [False, True, False],
            'expected_slice_result': bytearray(b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00'),
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
    assert bytearray(b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00') == result

def test_siabin_encoder():
    class Answer(SiabinEncoder):
        def __init__(self, number=0):
            self._number = number
        def siabin_encode(self):
            if self._number == 42:
                return encode(True)
            return encode(False)
    
    test_cases = [
        {
            'value': Answer(),
            'expected_result': bytearray(b'\x00'),
        },
        {
            'value': Answer(42),
            'expected_result': bytearray(b'\x01'),
        },
        {
            'value': Answer(43),
            'expected_result': bytearray(b'\x00'),
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
            'expected_result': bytearray(b'\x2A\x00\x00\x00\x00\x00\x00\x00\x01\x03\x00\x00\x00\x00\x00\x00\x00foo\x02\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),
        },
    ]

    for tc in test_cases:
        result = encode_all(*tc['values'])
        assert tc['expected_result'] == result

def test_encode_currency():
    test_cases = [
        {
            'value': 0,
            'expected_result': bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00'),
        },
        {
            'value': 5577006791947779410,
            'expected_result': bytearray(b'\x08\x00\x00\x00\x00\x00\x00\x00\x4d\x65\x82\x21\x07\xfc\xfd\x52'),
        },
        {
            'value': 35,
            'expected_result': bytearray(b'\x01\x00\x00\x00\x00\x00\x00\x00\x23'),
        },
        {
            'value': 8674665223082153551,
            'expected_result': bytearray(b'\x08\x00\x00\x00\x00\x00\x00\x00\x78\x62\x9a\x0f\x5f\x3f\x16\x4f'),
        },
        {
            'value': 1111111111111,
            'expected_result': bytearray(b'\x06\x00\x00\x00\x00\x00\x00\x00\x01\x02\xb3\x62\x11\xc7'),
        },
        {
            'value': 18446744073709551615,
            'expected_result': bytearray(b'\x08\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff'),
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
