

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

    kosmos 'j.data.types.test(name="duration")' --debug
    """

    return "OK"

    # TODO:*1

    self = j.data.types.get("duration")

    c = """
    1s
    2m
    3h
    4d
    1m2s
    1h2s
    1h2m
    1h2m3s
    1d2s
    1d2m
    1d2m3s
    1d2h
    1d2h3s
    1d2h3m
    1d2h3m4s
    """
    c = j.core.text.strip(c)
    for line in c.split("\n"):
        if line.strip() == "":
            continue
        seconds = self.clean(line)
        out = self.toString(seconds)
        print(out)
        assert line == out

    self.clean("'0'") == 0
    self.clean("'42'") == 42
    self.clean(None) == 0
    self.clean(23) == 23

    self._log_info("TEST DONE DURATION")

    return "OK"
