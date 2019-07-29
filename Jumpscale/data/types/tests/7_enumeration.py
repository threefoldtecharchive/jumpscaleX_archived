

# Copyright (C) 2019 :  TF TECH NV in Belgium see https://www.threefold.tech/
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.


from Jumpscale import j


def main(self):
    """
    to run:

    kosmos 'j.data.types.test(name="enumeration")'
    """

    e = j.data.types.get("e", default="yellow,blue,red")

    assert str(e) == "ENUM: YELLOW,BLUE,RED (default:YELLOW)"

    assert e.toString(2) == "BLUE"
    assert e.toString(3) == "RED"

    try:
        e.clean(4)
        raise RuntimeError("should not work")
    except Exception:
        pass

    str(e.clean(0)) == "UNKNOWN"

    assert e.toString(" blue") == "BLUE"
    assert e.toString("Red ") == "RED"

    assert str(e.clean("Red ")) == "RED"
    assert str(e.clean("BLUE ")) == "BLUE"
    assert str(e.clean("YELLOW ")) == "YELLOW"

    # start count from 1 (0 is for None)
    assert e.toData("BLUE ") == 2
    assert e.toData("Red ") == 3
    assert e.toData("YELLOW ") == 1

    assert e._jsx_location == "j.data.types._types['enum_b3fb5d69cff844ccc156a430ea82e83b']"
    e = j.data.types._types["enum_b3fb5d69cff844ccc156a430ea82e83b"]
    assert str(e) == "ENUM: YELLOW,BLUE,RED (default:YELLOW)"

    enum = e.clean(1)
    enum2 = e.clean(2)
    enum3 = e.clean(1)

    assert enum.value == 1

    assert enum == enum3
    assert enum != enum2

    assert e.RED == e.clean(3)
    assert e.RED == "RED"

    assert str(enum3) == "YELLOW"
    assert enum3.BLUE == enum2.BLUE
    assert str(enum3) == "BLUE"

    self._log_info("TEST DONE ENUMERATION")

    return "OK"
