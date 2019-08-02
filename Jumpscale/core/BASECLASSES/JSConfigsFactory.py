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


# is a factory for multiple JSConfig baseclasses
from Jumpscale import j
from .JSBase import JSBase

"""
factory for JSConfig & JSConfigs objects
"""

from .Attr import Attr


class JSConfigsFactory(JSBase, Attr):
    def __init_class_post(self):

        if not hasattr(self.__class__, "_CHILDCLASSES"):
            raise j.exceptions.Base("_CHILDCLASSES needs to be specified")

    def _init_pre2(self, **kwargs):

        if hasattr(self.__class__, "_CHILDCLASS"):
            # means we will only use 1 JSConfigs as child
            assert not hasattr(self.__class__, "_CHILDCLASSES")
            assert self.__class__._CHILDCLASS
            self.__class__._CHILDCLASSES = [self.__class__._CHILDCLASS]

        for kl in self.__class__._CHILDCLASSES:
            # childclasses are the JSConfigs classes

            if not kl._name:
                name = j.core.text.strip_to_ascii_dense(str(kl)).split(".")[-1].lower()
            else:
                name = kl._name
            assert name
            # self._log_debug("attach child:%s" % name)
            if issubclass(kl, j.application.JSBaseConfigClass):
                obj = kl(parent=self, name=name)
                assert obj._parent
            elif issubclass(kl, j.application.JSBaseConfigsClass):
                obj = kl(parent=self, name=name)
                assert obj._parent
            else:
                raise j.exceptions.Base("wrong childclass:%s" % kl)
            self._children[name] = obj

    def _init_post(self, **kwargs):
        self._protected = True

    def _obj_cache_reset(self):
        """
        make sure that all objects we remember inside are emptied
        :return:
        """
        JSBase._obj_cache_reset(self)
        for factory in self._children.values():
            factory._obj_cache_reset()

    def _bcdb_selector(self):
        """
        always uses the system BCDB, unless if this one implements something else
        """
        return j.application.bcdb_system

    def delete(self):
        for item in self._children_recursive_get():
            if isinstance(item, j.application.JSBaseConfigClass):
                self._log("delete:%s" % item.name)
                item.delete()
        if isinstance(self, j.application.JSBaseConfigClass):
            # means we delete our own config as well
            self.delete_()

    def save(self):
        for item in self._children_recursive_get():
            if isinstance(item, j.application.JSBaseConfigClass):
                self._log("save:%s" % item.name)
                item.save()
        if isinstance(self, j.application.JSBaseConfigClass):
            # means we save our own config as well
            self.save_()
