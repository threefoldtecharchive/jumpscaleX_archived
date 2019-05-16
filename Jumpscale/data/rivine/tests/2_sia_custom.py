from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.rivine.test(name="sia_custom")'
    """
    e = j.data.rivine.encoder_sia_get()

    # a class that provides a custom encoding logic for its types,
    # required in order to be able to encode Python objects
    class Answer(j.data.rivine.BaseSiaObjectEncoder):
        def __init__(self, number=0):
            self._number = number

        def sia_binary_encode(self, encoder):
            if self._number == 42:
                return encoder.add(True)
            return encoder.add(False)

    # when we add our objects they will be encoded
    # using the method as provided by its type
    e.add(Answer())
    e.add(Answer(42))

    # this works for slices and arrays as well
    e.add_array([Answer(5), Answer(2)])

    # the result is a single bytearray
    assert e.data == b"\x00\x01\x00\x00"
