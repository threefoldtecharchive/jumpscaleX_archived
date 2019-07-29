

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

    kosmos 'j.data.types.test(name="dict")'
    """

    e = j.data.types.get("dict")

    ddict = {}
    ddict["a"] = 1
    ddict["b"] = "b"

    ddict2 = e.clean(ddict)
    assert {"a": 1, "b": "b"} == ddict2

    assert j.data.types.dict.check(ddict2)

    data = e.toData(ddict2)

    assert {"a": 1, "b": "b"} == e.clean(data)

    assert e.toString(data) == '{\n "a": 1,\n "b": "b"\n}'

    datastr = e.toString(data)

    assert {"a": 1, "b": "b"} == e.clean(datastr)

    return "OK"
