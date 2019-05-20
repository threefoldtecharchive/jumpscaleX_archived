from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.rivine.test(name="sia_types")'
    """
    e = j.data.rivine.encoder_sia_get()

    # in the sia_basic test we saw we can
    # serialise anything using the add method.

    # by default strings, byte arrays and iterateable objects
    # are encoded as slices.
    #
    # array are like slices, but have no length prefix,
    # therefore this is only useful if there is a fixed amount of elements,
    # known by all parties
    e.add_array([False, True, True])

    # a single byte can be added as well
    e.add_byte(6)
    e.add_byte("4")
    e.add_byte(b"2")

    # the result is a single bytearray
    assert e.data == b"\x00\x01\x01\x0642"
