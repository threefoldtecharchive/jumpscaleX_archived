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
from .JSConfigBase import JSConfigBase


class JSConfigs(JSConfigBase):
    def _init_pre(self, **kwargs):
        self._triggers = []
        self._model_ = None

    def _process_schematext(self, schematext):
        """
        rewrites the schema in such way there is always a parent_id and name
        :param schematext:
        :return:
        """
        assert schematext
        schematext = j.core.tools.text_strip(schematext, replace=False)
        if schematext.find("name") == -1:
            if "\n" != schematext[-1]:
                schematext += "\n"
            schematext += 'name* = ""\n'
        if isinstance(self._parent, j.application.JSConfigClass):
            if schematext.find("parent_id") == -1:
                if "\n" != schematext[-1]:
                    schematext += "\n"
                schematext += "parent_id* = 0 (I)\n"
        return schematext

    @property
    def _model(self):
        if self._model_ is None:
            # self._log_debug("Get model for %s"%self.__class__._location)
            bcdb = self._bcdb_selector()
            if "_SCHEMATEXT" in self.__class__.__dict__:
                s = self.__class__._SCHEMATEXT
            else:
                s = self.__class__._CHILDCLASS._SCHEMATEXT
            t = self._process_schematext(s)
            self._model_ = bcdb.model_get(schema=t)
        return self._model_

    def _bcdb_selector(self):
        """
        always uses the system BCDB, unless if this one implements something else
        """
        if self._parent and hasattr(self._parent, "_bcdb_selector"):
            # relevant in case the parent is JSConfigsFactory
            return self._parent._bcdb_selector()
        else:
            return j.application.bcdb_system

    def _childclass_selector(self, jsxobject, **kwargs):
        """
        allow custom implementation of which child class to use
        :return:
        """
        return self.__class__._CHILDCLASS

    def new(self, name, jsxobject=None, save=True, delete=True, **kwargs):
        """
        it it exists will delete if first when delete == True
        :param name:
        :param jsxobject:
        :param save:
        :param kwargs:
        :return:
        """
        if delete:
            self.delete(name)
        else:
            if self.exists(name=name):
                raise j.exceptions.Base("cannot do new object, exists")
        return self._new(name=name, jsxobject=jsxobject, save=save, **kwargs)

    def _new(self, name, jsxobject=None, save=True, **kwargs):
        """
        :param name: for the CONFIG item (is a unique name for the service, client, ...)
        :param jsxobject: you can right away specify the jsxobject
        :param kwargs: the data elements which will be given to JSXObject underneith (given to constructor)
        :return: the service
        """
        if not jsxobject:
            jsxobject = self._model.new(data=kwargs)
            jsxobject.name = name

        # means we need to remember the parent id
        if isinstance(self._parent, j.application.JSConfigClass):
            if not self._parent._id:
                self._parent.save()
                assert self._parent._id
            jsxobject.parent_id = self._parent._id

        jsconfig_klass = self._childclass_selector(jsxobject=jsxobject)
        jsconfig = jsconfig_klass(parent=self, jsxobject=jsxobject)
        jsconfig._triggers_call(jsconfig, "new")
        self._children[name] = jsconfig
        if save and not jsxobject:
            self._children[name].save()
            self._children[name]._autosave = True
        return self._children[name]

    def get(self, name="main", needexist=False, save=True, **kwargs):
        """
        :param name: of the object
        """

        jsconfig = self._get(name=name, die=needexist)

        if not jsconfig:
            self._log_debug("NEW OBJ:%s:%s" % (name, self._name))
            jsconfig = self._new(name=name, save=save, **kwargs)
        else:
            # check that the stored values correspond with kwargs given
            changed = False
            for key, val in kwargs.items():
                if not getattr(jsconfig, key) == val:
                    changed = True
                    setattr(jsconfig, key, val)
                    # msg = "COULD NOT GET OBJ BECAUSE KWARGS GIVEN DO NOT CORRESPOND WITH OBJ IN DB\n"
                    # msg += "kwargs: key:%s val:%s\n" % (key, val)
                    # msg += "object was:\n%s\n" % jsconfig._data._ddict_hr_get()
                    # raise j.exceptions.Base(msg)
            if changed and save:
                jsconfig.save()

        jsconfig._triggers_call(jsconfig, "get")
        return jsconfig

    def _get(self, name="main", die=True):
        assert name
        if name in self._children:
            return self._children[name]

        self._log_debug("get child:'%s'from '%s'" % (name, self._name))

        # new = False
        res = self.find(name=name)

        if len(res) < 1:
            if not die:
                return
            raise j.exceptions.Base(
                "Did not find instance for:%s, name searched for:%s" % (self.__class__._location, name)
            )

        elif len(res) > 1:
            raise j.exceptions.Base(
                "Found more than 1 service for :%s, name searched for:%s" % (self.__class__._location, name)
            )
        else:
            jsxconfig = res[0]

        return jsxconfig

    def reset(self):
        """
        will destroy all data in the DB, be carefull
        :return:
        """
        self._log_debug("reset all data")
        for item in self.find():
            item.delete()
        self._children = {}

    def find(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the config objects
        """
        res = []
        for key, item in self._children.items():
            match = True
            for key, val in kwargs.items():
                if hasattr(item, key):
                    if val != getattr(item, key):
                        match = False
                else:
                    raise j.exceptions.Value("could not find for prop:%s, did not exist in %s" % (key, self._key))
            if match:
                res.append(item)

        for jsxobject in self._findData(**kwargs):
            name = jsxobject.name
            if not name in self._children:
                r = self._new(name=name, jsxobject=jsxobject)
                res.append(r)
        return res

    def count(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the config objects
        """
        return len(self._findData(**kwargs))

    def _findData(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the data objects (the data of the model)
        """

        if isinstance(self._parent, j.application.JSConfigClass):
            if not self._parent._id:
                self._parent.save()
                assert self._parent._id
            kwargs["parent_id"] = str(self._parent._id)

        if len(kwargs) > 0:
            propnames = [i for i in kwargs.keys()]
            propnames_keys_in_schema = [
                item.name for item in self._model.schema.properties_index_keys if item.name in propnames
            ]
            if len(propnames_keys_in_schema) > 0:
                # we can try to find this config
                return self._model.find(**kwargs)
            else:
                raise j.exceptions.Base(
                    "cannot find obj with kwargs:\n%s\n in %s\nbecause kwargs do not match, is there * in schema"
                    % (kwargs, self)
                )
            return []
        else:
            return self._model.find()

    def delete(self, name):
        if name in self._children:
            self._children.pop(name)
        res = self._findData(name=name)
        if len(res) == 0:
            return
        elif len(res) == 1:
            self._model.delete(res[0].id)

    def exists(self, name="main"):
        """
        :param name: of the object
        """
        if name in self._children:
            return True
        res = self._findData(name=name)
        if len(res) > 1:
            raise j.exceptions.Base(
                "found too many items for :%s, name:\n%s\n%s" % (self.__class__.__name__, name, res)
            )
        elif len(res) == 1:
            return True
        else:
            return False

    def _children_names_get(self, filter=None):
        """
        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        :param self:
        :param filter:
        :return:
        """

        def do():
            x = []
            for key, item in self._children.items():
                x.append(key)
            for item in self._findData():
                if item.name not in x:
                    x.append(item.name)
            return x

        x = self._cache.get(key="_children_names_get", method=do, expire=10)  # will redo every 10 sec
        return self._filter(filter=filter, llist=x, nameonly=True)

    def _children_get(self, filter=None):
        """
        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        :return:
        """
        x = []
        for key, item in self._children.items():
            x.append(item)
        for item in self.find():
            if item not in x:
                x.append(item)
        return self._filter(filter=filter, llist=x, nameonly=False)
