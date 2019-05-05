from Jumpscale import j
import pytest

def main(self):
    """
    to run:

    kosmos 'j.data.schema.test(name="unittests")' --debug
    """
    unittests_path = "/sandbox/code/github/threefoldtech/jumpscaleX/Jumpscale/data/schema/tests/testsuite"
    assert pytest.main([unittests_path]) == 0
