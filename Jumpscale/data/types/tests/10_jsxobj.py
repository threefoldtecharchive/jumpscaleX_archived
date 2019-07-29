

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

    kosmos 'j.data.types.test(name="jsxobj")' --debug
    """

    schema = """
        @url = despiegk.test
        llist = []
        llist2 = "" (LS) #L means = list, S=String
        llist3 = [1,2,3] (LF)
        nr = 4
        date_start = 0 (D)
        description = "test"        
        llist4 = [1,2,3] (L)
        llist5 = [1,2,3] (LI)
        llist6 = "1,2,3" (LI)
        U = 0.0
        """

    schema_object = j.data.schema.get_from_text(schema_text=schema)

    tt = j.data.types.get("o", "despiegk.test")

    assert tt._schema._md5 == schema_object._md5

    assert tt.BASETYPE == "JSXOBJ"

    o = tt.clean({})

    assert o.nr == 4
    assert tt.check(o)

    o2 = tt.clean({"nr": 5})
    assert o2.nr == 5

    o3 = tt.default_get()

    print(tt._schema._capnp_schema_text)

    assert o3 == tt.clean(o3)

    print(o3._ddict)
    print(o3)

    assert o3.description == "test"

    tt = j.data.types.get("lo", "despiegk.test")

    ll = tt.clean()

    o = ll.new()
    o.U = 1

    assert ll[0].U == 1

    assert ll._child_type.BASETYPE == "JSXOBJ"

    print(o)

    self._log_info("TEST DONE JSXOBJ")

    return "OK"
