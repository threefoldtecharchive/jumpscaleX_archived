

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

    kosmos 'j.data.types.test(name="datetime")'
    """

    tt = j.data.types.datetime

    c = """
    11/30 22:50
    11/30
    1990/11/30
    1990/11/30 10am:50
    1990/11/30 10pm:50
    1990/11/30 22:50
    30/11/1990
    30/11/1990 10pm:50
    """
    c = j.core.text.strip(c)
    out = ""
    for line in c.split("\n"):
        if line.strip() == "":
            continue
        epoch = tt.clean(line)
        out += "%s -> %s\n" % (line, tt.toString(epoch))
    out_compare = """
    11/30 22:50 -> 2019/11/30 22:50:00
    11/30 -> 2019/11/30 00:00:00
    1990/11/30 -> 1990/11/30 00:00:00
    1990/11/30 10am:50 -> 1990/11/30 10:50:00
    1990/11/30 10pm:50 -> 1990/11/30 22:50:00
    1990/11/30 22:50 -> 1990/11/30 22:50:00
    30/11/1990 -> 1990/11/30 00:00:00
    30/11/1990 10pm:50 -> 1990/11/30 22:50:00
    """
    print(out)
    out = j.core.text.strip(out)
    out_compare = j.core.text.strip(out_compare)
    assert out == out_compare

    assert tt.clean(0) == 0

    tt.clean("-0s") == j.data.time.epoch

    tt.clean("'0'") == 0

    print("test j.data.types.date.datetime() ok")

    tt = j.data.types.date

    c = """
    11/30
    1990/11/30
    30/11/1990
    """
    c = j.core.text.strip(c)
    out = ""
    for line in c.split("\n"):
        if line.strip() == "":
            continue
        epoch = tt.clean(line)
        out += "%s -> %s\n" % (line, tt.toString(epoch))
    out_compare = """
    11/30 -> 2019/11/30
    1990/11/30 -> 1990/11/30
    30/11/1990 -> 1990/11/30
    """
    print(out)
    out = j.core.text.strip(out)
    out_compare = j.core.text.strip(out_compare)
    assert out == out_compare

    assert tt.clean(0) == 0
    assert tt.clean("") == 0

    tt.clean("-0s") == j.data.time.epoch

    print("test j.data.types.date.test() ok")

    # tt._log_info("TEST DONE")

    return "OK"
