from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.types.test(name="base")'
    """


    assert j.data.types.s.__class__.NAME == 'str,s,string'

    assert j.data.types.get("s") == j.data.types.get("string")

    j.shell()

    #TODO: need more tests here

    self._log_info("TEST DONE")

    return ("OK")
