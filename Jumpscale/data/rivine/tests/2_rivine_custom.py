from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.rivine.test(name="rivine_custom")'
    """
    e = j.data.rivine.encoder_rivine_get()

    # a class that provides a custom encoding logic for its types,
    # required in order to be able to encode Python objects
    class Answer(j.data.rivine.BaseRivineObjectEncoder):
        def __init__(self, number=0):
            self._number = number

        def rivine_binary_encode(self, encoder):
            if self._number % 2 != 0:
                return encoder.add_int24(self._number - 1)
            return encoder.add_int24(self._number)

    # when we add our objects they will be encoded
    # using the method as provided by its type
    e.add(Answer())
    e.add(Answer(43))

    # this works for slices and arrays as well
    e.add_array([Answer(5), Answer(2)])

    # the result is a single bytearray
    assert e.data == b"\x00\x00\x00\x2A\x00\x00\x04\x00\x00\x02\x00\x00"
