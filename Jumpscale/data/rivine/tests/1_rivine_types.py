from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.rivine.test(name="rivine_types")'
    """
    e = j.data.rivine.encoder_rivine_get()

    # in the rivine_basic test we saw we can
    # serialise anything using the add method.
    # One can however also directly encode the specific type as desired,
    # which allows for example the encoding of an integer as a specific byte size.
    e.add_int8(1)
    e.add_int16(2)
    e.add_int24(3)
    e.add_int32(4)
    e.add_int64(5)

    # a single byte can be added as well
    e.add_byte(6)
    e.add_byte("4")
    e.add_byte(b"2")

    # array are like slices, but have no length prefix,
    # therefore this is only useful if there is a fixed amount of elements,
    # known by all parties
    e.add_array([False, True, True])

    # the result is a single bytearray
    assert e.data == b"\x01\x02\x00\x03\x00\x00\x04\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x0642\x00\x01\x01"
