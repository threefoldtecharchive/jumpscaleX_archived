# Copyright (C) July 2018:  TF TECH NV in Belgium see https://www.threefold.tech/
# In case TF TECH NV ceases to exist (e.g. because of bankruptcy)
#   then Incubaid NV also in Belgium will get the Copyright & Authorship for all changes made since July 2018
#   and the license will automatically become Apache v2 for all code related to Jumpscale & DigitalMe
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
# LICENSE END


from Jumpscale import j

### CLASS DEALING WITH THE ATTRIBUTES SET & GET


class Children:
    def __init__(self):
        self._children = {}

    def _add(self, name, child):
        name = name + ""
        self._children[name] = child

    def __getattr__(self, name):

        if name in self._children:
            return self._children[name]

        return self.__getattribute__(name)

    def __setattr__(self, key, value):

        if key.startswith("_"):
            self.__dict__[key] = value
            return

        raise j.exceptions.Base("protected property:%s" % key)
