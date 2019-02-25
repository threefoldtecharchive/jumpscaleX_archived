from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.types.test(name="hash")'
    """

    e = j.data.types.get("h")

    assert e.default_get() == (0, 0)
    assert e.clean("1:2") == (1,2)

    return ("OK")
