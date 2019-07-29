

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

    kosmos 'j.data.types.test(name="list")'
    """

    tt = j.data.types.get("l", default="1,2,3")  # should return list of strings

    C = """
    - 1
    - 2
    - 3
    """
    C = j.core.text.strip(C).strip()
    str(tt.default_get()).strip() == C

    l = tt.clean(val="3,4,5")

    assert l[1] == "4"
    # l is now a list of strings

    tt = j.data.types.get("li", default="1,2,3")  # should be a list of integers
    l = tt.clean(val="3,4,5")

    assert l[1] == 4

    assert 4 in l
    assert not "4" in l

    l = tt.default_get()
    C = """
    - 1
    - 2
    - 3
    """
    C = j.core.text.strip(C).strip()
    assert str(l).strip() == C
    l = tt.clean(l[:])  # avoid manipulating list factory default
    l.append(4)
    l.append("5")

    assert l == [1, 2, 3, 4, 5]
    assert len(l) == 5

    assert 5 in l

    l[1] = 10
    assert l == [1, 10, 3, 4, 5]
    assert len(l) == 5

    self._log_info("TEST DONE LIST")

    return "OK"
