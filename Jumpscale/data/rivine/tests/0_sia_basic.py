from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.rivine.test(name="sia_basic")'
    """
    e = j.data.rivine.encoder_sia_get()

    # you can add integers, booleans, iterateble objects, strings,
    # bytes and byte arrays. Dictionaries and objects are not supported.
    e.add(False)
    e.add("a")
    e.add([1, True, "foo"])
    e.add(b"123")

    # the result is a single bytearray
    assert (
        e.data
        == b"\x00\x01\x00\x00\x00\x00\x00\x00\x00a\x03\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x03\x00\x00\x00\x00\x00\x00\x00foo\x03\x00\x00\x00\x00\x00\x00\x00123"
    )
