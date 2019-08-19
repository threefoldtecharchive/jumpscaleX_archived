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
from .JSBase import JSBase

"""
classes who use JSXObject for data storage but provide nice interface to enduser
"""

from .Attr import Attr


class JSConfigBase(JSBase, Attr):
    def _init_post(self, **kwargs):
        # I THINK THIS CAN BE MOVED TO __init_class_post (LETS DO LATER)
        props, methods = self._inspect()
        self._properties_ = props
        self._methods_ = methods
        self._protected = True

    def __init_class_post(self):

        if isinstance(j.application.JSBaseConfigClass) and isinstance(j.application.JSBaseConfigsClass):
            raise j.exceptions.Base("combination not allowed of config and configsclass")

    def _obj_cache_reset(self):
        JSBase._obj_cache_reset(self)
        # IS THIS RIGHT?
        for key, obj in self._children.items():
            del self._children[key]
            self._children.pop(key)

    #### NEED TO IMPLEMENT BUT THINK FIRST

    def _trigger_add(self, method):
        """

        triggers are called with (jsconfigs, jsconfig, action, propertyname=None)

        can register any method you want to respond on some change

        - jsconfigs: if relevant the factory starting drom model to 1 instance
        - jsconfig: the jsconfig object
        - action: e.g. new, delete, get, stop, ...  (any method call)
        - propertyname if the trigger was called because of change of the property of the data underneith

        return: jsconfig object
        """
        if method not in self._triggers:
            self._triggers.append(method)

    def _triggers_call(self, jsconfig, action=None):
        """
        will go over all triggers and call them with arguments given

        """
        assert isinstance(jsconfig, j.application.JSConfigClass)
        self._log_debug("trigger: %s:%s" % (jsconfig.name, action))
        for method in self._triggers:
            jsconfig = method(jsconfigs=self, jsconfig=jsconfig, action=action)
            assert isinstance(jsconfig, j.application.JSConfigClass)
        return jsconfig
