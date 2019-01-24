from Jumpscale import j


def main(self):
    """
    to run:

    js_shell 'j.data.types.test(name="hash")'
    """

    e = j.data.types.get("h")

    assert e.get_default() == (0, 0)
    assert e.clean("1:2") == (1,2)

    return ("OK")
