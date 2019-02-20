from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.types.test(name="base")'
    """

    assert j.data.types.s.__class__.NAME == "string"

    assert j.data.types.get("s") == j.data.types.get("string")

    #TODO: need more tests here

    self._log_info("TEST DONE")

    return ("OK")
