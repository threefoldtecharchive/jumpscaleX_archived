from Jumpscale import j
import pytest
from Jumpscale.data.rivine.RivineBinaryEncoder import IntegerOutOfRange, SliceLengthOutOfRange


def main(self):
    """
    to run:

    kosmos 'j.data.rivine.test(name="rivine_limits")'
    """
    e = j.data.rivine.encoder_rivine_get()

    # everything has limits, so do types,
    # that is what this test is about

    # no integer can be negative
    with pytest.raises(IntegerOutOfRange):
        e.add(-1)
    with pytest.raises(IntegerOutOfRange):
        e.add_int64(-1)
    with pytest.raises(IntegerOutOfRange):
        e.add_int32(-1)
    with pytest.raises(IntegerOutOfRange):
        e.add_int24(-1)
    with pytest.raises(IntegerOutOfRange):
        e.add_int16(-1)
    with pytest.raises(IntegerOutOfRange):
        e.add_int8(-1)

    # integers have upper limits as well
    with pytest.raises(IntegerOutOfRange):
        e.add(1 << 64)
    with pytest.raises(IntegerOutOfRange):
        e.add_int64(1 << 64)
    with pytest.raises(IntegerOutOfRange):
        e.add_int32(1 << 32)
    with pytest.raises(IntegerOutOfRange):
        e.add_int24(1 << 24)
    with pytest.raises(IntegerOutOfRange):
        e.add_int16(1 << 16)
    with pytest.raises(IntegerOutOfRange):
        e.add_int8(1 << 8)

    # slices have limits too,
    # but should you ever user (1<<29) or more objects,
    # you have other things to worry about
