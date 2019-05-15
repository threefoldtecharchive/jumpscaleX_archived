from Jumpscale import j
import pytest
from Jumpscale.data.rivine.SiaBinaryEncoder import IntegerOutOfRange


def main(self):
    """
    to run:

    kosmos 'j.data.rivine.test(name="sia_limits")'
    """
    e = j.data.rivine.encoder_sia_get()

    # everything has limits, so do types,
    # that is what this test is about

    # no integer can be negative
    with pytest.raises(IntegerOutOfRange):
        e.add(-1)
    # integers have an upper bound
    with pytest.raises(IntegerOutOfRange):
        e.add(1 << 64)
