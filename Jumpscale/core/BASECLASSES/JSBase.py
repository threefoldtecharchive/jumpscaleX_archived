

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
import os

# import copy
# import sys
import inspect
import types

"""
the lowest level class, every object in Jumpscale inherits from this one

functions

- logging
- initialization of the class level stuff
- caching logic
- logic for auto completion in shell
- state on execution of methods (the _done methods)

"""


class JSBase:

    __init_class_done = False
    _protected = False
    _dirpath_ = ""
    # _objcat_name = ""
    _cache_expiration = 3600
    _test_runs = {}
    _test_runs_error = {}
    _name = ""
    _location = ""
    _logger_min_level = 10
    _class_children = []
    _properties = []

    def __init__(self, parent=None, **kwargs):
        """
        :param parent: parent is object calling us
        :param topclass: if True means no-one inherits from us
        """

        self._protected = False
        self._parent = parent
        self._children = {}
        if "parent" in kwargs:
            kwargs.pop("parent")
        self._init_pre(**kwargs)
        self._init_pre2(**kwargs)
        self.__init_class()
        self._obj_cache_reset()
        self._init(**kwargs)
        props, methods = self._inspect()
        self._properties = props
        self._init_post(**kwargs)

    def __init_class(self):

        if not self.__class__.__init_class_done:

            # short location name:

            if not self.__class__._name:
                self.__class__._name = j.core.text.strip_to_ascii_dense(str(self.__class__)).split(".")[-1].lower()
                # name = str(self.__class__).split(".")[-1].split("'", 1)[0].lower()  # wonder if there is no better way

            if "__jslocation__" in self.__dict__:
                self.__class__._location = self.__jslocation__
            elif "__jslocation__" in self.__class__.__dict__:
                self.__class__._location = self.__class__.__jslocation__
            elif "__jscorelocation__" in self.__dict__:
                self.__class__._location = self.__jslocation__
            else:
                self.__class__._location = None
                parent = self._parent
                while parent is not None:
                    if "__jslocation__" in parent.__dict__:
                        # if hasattr(parent, "__jslocation__"):
                        self.__class__._location = parent.__jslocation__
                        break
                    parent = parent._parent
                if self.__class__._location is None:
                    self.__class__._location = self.__class__._name

            # # walk to all parents, let them know that there are child classes
            # self.__class__._class_children = []
            # parent = self._parent
            # while parent is not None:
            #     if parent.__class__ not in parent._class_children:
            #         parent._class_children.append(parent.__class__)
            #     parent = parent._parent

            # if self.__class__._location.lower() != self.__class__._name.lower():
            #     self.__class__._key = "%s:%s" % (self.__class__._location, self.__class__._name)
            # else:
            #     self.__class__._key = self.__class__._name.lower()

            self.__init_class_post()

            self.__class__.__init_class_done = True

            self._log_debug("***CLASS INIT 1: %s" % self.__class__._name)

            # lets make sure the initial loglevel gets set
            self._logger_set(children=False, parents=False)

    def __init_class_post(self):
        pass

    def _inspect(self, include_prefix=None, exclude_prefix=None):
        """

        returns properties and methods of the class/object

        properties,methods = self._inspect()

        :return: (properties,methods)
        """
        # self._log("INSPECT:%s" % self.__class__)
        properties = []
        methods = []
        for name, obj in inspect.getmembers(self.__class__):
            if include_prefix and not name.startswith(include_prefix):
                continue
            if exclude_prefix and name.startswith(exclude_prefix):
                continue
            if inspect.ismethod(obj):
                methods.append(name)
            elif inspect.ismethoddescriptor(obj):
                continue
            elif inspect.isfunction(obj):
                methods.append(name)
            elif inspect.isclass(obj):
                properties.append(name)
            elif inspect.isgetsetdescriptor(obj):
                continue
            else:
                properties.append(name)

        for item in self.__dict__.keys():
            if include_prefix and not name.startswith(include_prefix):
                continue
            if exclude_prefix and name.startswith(exclude_prefix):
                continue
            if item not in properties:
                properties.append(item)
        return properties, methods

    @property
    def _key(self):
        return self._name

    def _logging_enable_check(self):
        """

        check if logging should be disabled for current js location

        according to logger includes and excludes (configured)
        includes have a higher priority over excludes

        will not take minlevel into consideration, its only the excludes & includes

        :return: True if logging is enabled
        :rtype: bool
        """
        if j.core.myenv.config.get("DEBUG", False):
            return True

        def check(checkitems):
            for finditem in checkitems:
                finditem = finditem.strip().lower()
                if finditem == "*":
                    return True
                if finditem == "":
                    continue
                if "*" in finditem:
                    if finditem[-1] == "*":
                        # means at end
                        if self._key.startswith(finditem[:-1]):
                            return True
                    elif finditem[0] == "*":
                        if self._key.endswith(finditem[1:]):
                            return True
                    else:
                        raise RuntimeError("find item can only have * at start or at end")
                else:
                    if self._key == finditem:
                        return True
            return False

        if check(j.core.myenv.log_includes) and not check(j.core.myenv.log_excludes):
            return True
        return False

    def _logger_set(self, minlevel=None, children=True, parents=True):
        """

        :param min_level if not set then will use the LOGGER_LEVEL from /sandbox/cfg/jumpscale_config.toml

        make sure that logging above minlevel will happen, std = 100
        if 100 means will not log anything


        - CRITICAL 	50
        - ERROR 	40
        - WARNING 	30
        - INFO 	    20
        - STDOUT 	15
        - DEBUG 	10
        - NOTSET 	0


        if parents and children: will be set on all classes of the self.location e.g. j.clients.ssh (children, ...)

        if minlevel specified then it will always consider the logging to be enabled

        :return:
        """
        if minlevel is not None or self._logging_enable_check():
            # if minlevel specified we overrule anything

            # print ("%s:loginit"%self.__class__._name)
            if minlevel is None:
                minlevel = int(j.core.myenv.config.get("LOGGER_LEVEL", 15))

            if minlevel is not None or not self._logging_enable_check():

                self.__class__._logger_min_level = minlevel

                if parents:
                    parent = self._parent
                    while parent is not None:
                        parent._logger_set(minlevel=minlevel)
                        parent = parent._parent

                if children:

                    for kl in self.__class__._class_children:
                        # print("%s:minlevel:%s"%(kl,minlevel))
                        kl._logger_min_level = minlevel

    def _init(self, **kwargs):
        pass

    def _init_pre(self, **kwargs):
        """
        meant to be used by developers of the base classes
        :return:
        """
        pass

    def _init_pre2(self, **kwargs):
        """
        meant to be used by developers of the base classes
        :return:
        """
        pass

    def _init_post(self, **kwargs):
        """
        meant to be used by developers of the base classes
        :return:
        """
        pass

    def _obj_cache_reset(self):
        """
        this empties the runtime state of an obj and the logger and the testruns
        :return:
        """

        self.__class__._test_runs = {}
        self._cache_ = None
        self._objid_ = None

        for key, obj in self.__dict__.items():
            del obj

    @property
    def _dirpath(self):
        if self.__class__._dirpath_ == "":
            self.__class__._dirpath_ = os.path.dirname(inspect.getfile(self.__class__))

            if not self.__class__._dirpath_:
                self.__class__._dirpath_ = j.sal.fs.getcwd()

        return self.__class__._dirpath_

    @property
    def _objid(self):
        if self._objid_ is None:
            id = self.__class__._location
            id2 = ""
            if "_data" in self.__dict__:
                try:
                    id2 = self._data.name
                except:
                    pass
                if id2 == "":
                    try:
                        if self._data.id is not None:
                            id2 = self._data.id
                    except:
                        pass
            if id2 == "":
                for item in ["instance", "_instance", "_id", "id", "name", "_name"]:
                    if item in self.__dict__ and self.__dict__[item]:
                        self._log_debug("found extra for obj_id")
                        id2 = str(self.__dict__[item])
                        break
            if id2 != "":
                self._objid_ = "%s_%s" % (id, id2)
            else:
                self._objid_ = id
        return self._objid_

    def _logger_enable(self):
        self._logger_set(0)

    @property
    def _cache(self):
        if self._cache_ is None:
            self._cache_ = j.core.cache.get(self._objid, expiration=self._cache_expiration)
        return self._cache_

    @property
    def _ddict(self):
        res = {}
        for key in self.__dict__.keys():
            if not key.startswith("_"):
                v = self.__dict__[key]
                if not isinstance(v, types.MethodType):
                    res[key] = v
        return res

    def __check(self):
        for key in self.__dict__.keys():
            if key not in self.__class__._names_properties_:
                raise RuntimeError("a property was inserted which should not be there")

    ################

    def _print(self, msg, cat=""):
        self._log(msg, cat=cat, level=15)

    def _log_debug(self, msg, cat="", data=None, context=None, _levelup=1):
        self._log(msg, cat=cat, level=10, data=data, context=context, _levelup=_levelup)

    def _log_info(self, msg, cat="", data=None, context=None, _levelup=1):
        self._log(msg, cat=cat, level=20, data=data, context=context, _levelup=_levelup)

    def _log_warning(self, msg, cat="", data=None, context=None, _levelup=1):
        self._log(msg, cat=cat, level=30, data=data, context=context, _levelup=_levelup)

    def _log_error(self, msg, cat="", data=None, context=None, _levelup=1):
        self._log(msg, cat=cat, level=40, data=data, context=context, _levelup=_levelup)

    def _log_critical(self, msg, cat="", data=None, context=None, _levelup=1):
        self._log(msg, cat=cat, level=50, data=data, context=context, _levelup=_levelup)

    def _log(self, msg, cat="", level=10, data=None, context=None, _levelup=1):
        """

        :param msg: what you want to log
        :param cat: any dot notation category
        :param level: level of the log
        :return:

        can use {RED}, {RESET}, ... see color codes

        levels:

        - CRITICAL 	50
        - ERROR 	40
        - WARNING 	30
        - INFO 	    20
        - STDOUT 	15
        - DEBUG 	10

        """

        if j.application.debug or self.__class__._logger_min_level - 1 < level:
            # now we will log

            frame_ = inspect.currentframe().f_back
            levelup = 0
            while frame_ and levelup < _levelup:
                frame_ = frame_.f_back
                levelup += 1

            fname = frame_.f_code.co_filename.split("/")[-1]
            defname = frame_.f_code.co_name
            linenr = frame_.f_lineno

            # while obj is None and frame_:
            #     locals_ = frame_.f_locals
            #
            #     if tbc2 in locals_:
            #         obj = locals_[tbc2]
            #     else:
            #         frame_ = frame_.f_back

            # if self._location not in [None,""]:
            #     if not self._location.endswith(self._name):
            #         context = "%s:%s:%s"%(self._location,self._name,defname)
            #     else:
            #         context = "%s:%s"%(self._location,defname)
            # if context=="":
            #     context = defname

            logdict = {}
            logdict["linenr"] = linenr
            logdict["processid"] = j.application.appname
            logdict["message"] = msg
            logdict["filepath"] = fname
            logdict["level"] = level
            if context:
                logdict["context"] = context
            else:
                try:
                    logdict["context"] = self._key
                except Exception as e:
                    logdict["context"] = ""
                    pass  # TODO:*1 is not good
            logdict["cat"] = cat

            logdict["use_custom_printer"] = j.application._in_autocomplete

            logdict["data"] = data
            if data and isinstance(data, dict):
                # shallow copy the data to avoid changing the original data
                hidden_data = data.copy()
                if "password" in data or "secret" in data or "passwd" in data:
                    hidden_data["password"] = "***"
                logdict["data"] = hidden_data

            j.core.tools.log2stdout(logdict)

    ################

    def _done_key(self, name):
        if name == "":
            key = self._objid
        else:
            key = "%s:%s" % (self._objid, name)
        return key

    def _done_check(self, name="", reset=False):
        if reset:
            self._done_delete(name=name)
        return j.core.myenv.state_get(self._done_key(name))
        # return j.core.db.hexists("done", key)

    def _done_set(self, name=""):
        j.core.myenv.state_set(self._done_key(name))
        # return j.core.db.hset("done", self._done_key(name), value)

    def _done_delete(self, name=""):
        j.core.myenv.state_delete(self._done_key(name))
        # return j.core.db.hset("done", self._done_key(name), value)

    def _done_reset(self):
        """
        if name =="" then will remove all from this object
        :param name:
        :return:
        """
        name = self._done_key("")
        j.core.myenv.states_delete(name)
        # if name == "":
        #     for item in j.core.db.hkeys("done"):
        #         item = item.decode()
        #         # print("reset todo:%s" % item)
        #         if item.find(self._objid) != -1:
        #             j.core.db.hdel("done", item)
        #             # print("reset did:%s" % item)
        # else:
        #     return j.core.db.hdel("done", "%s:%s" % (self._objid, name))

    ################### mechanisms for autocompletion in kosmos

    def __name_get(self, item):
        """
        helper mechanism to come to name
        """
        if isinstance(item, str) or isinstance(item, int):
            name = str(item)
        elif "name" in item.__dict__:
            name = item.name
        else:
            name = item._objid
        return name

    def _filter(self, filter=None, llist=[], nameonly=True, unique=True, sort=True):
        """

        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match
        :param llist:
        :param nameonly: will not return the items of the list but names derived from the list members
        :param unique: will make sure there are no duplicates
        :param sort: sort but only when nameonly
        :return:
        """
        res = []
        for item in llist:
            name = self.__name_get(item)
            if not name:
                continue
            if name.startswith("_JSBase"):
                continue
            if filter:
                if not filter.startswith("_") and name.startswith("_"):
                    continue
                if filter.endswith("*"):
                    filter2 = filter[:-1]
                    if not name.startswith(filter2):
                        continue
                elif filter.startswith("*"):
                    filter2 = filter[1:]
                    if not name.endswith(filter2):
                        continue
                elif filter.startswith("R"):
                    j.shell()
                    filter3 = filter[1:]
                    w
                else:
                    if not name == filter:
                        continue
            else:
                if name.startswith("_"):
                    continue

            if nameonly:
                item = name
            if unique:
                if item not in res:
                    res.append(item)
            else:
                res.append(item)

        if nameonly and sort:
            res.sort()

        return res

    def _parent_name_get(self):
        if self._parent:
            return self.__name_get(self._parent)
        return ""

    def _children_names_get(self, filter=None):
        return self._filter(filter=filter, llist=self._children_get(filter=filter))

    def _children_get(self, filter=None):
        """
        if nothing then is self._children

        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        :return:
        """
        children = self._children.values()
        return self._filter(filter=filter, llist=children, nameonly=False)

    def _child_get(self, name=None, id=None):
        """
        finds a child based on name or id
        :param name:
        :param id:
        :return:
        """
        for item in self._children_get():
            if name:
                assert isinstance(name, str)
                if self.__name_get(item) == name:
                    return item
            elif id:
                id = int(id)
                if item.id == id:
                    return item
            else:
                raise RuntimeError("need to specify name or id")
        return None

    def _dataprops_names_get(self, filter=None):
        """
        e.g. in a JSConfig object would be the names of properties of the jsxobject = data
        e.g. in a JSXObject would be the names of the properties of the data itself

        :return: list of the names
        """
        # return self._filter(filter=filter, llist=self._names_methods_)
        return []

    def _methods_names_get(self, filter=None):
        """
        return the names of the methods which were defined at __init__ level by the developer

        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        """
        properties, methods = self._inspect()
        return self._filter(filter=filter, llist=methods)

    def _properties_names_get(self, filter=None):
        """
        return the names of the properties which were defined at __init__ level by the developer

        :param filter: is '' then will show all, if None will ignore _
                when * at end it will be considered a prefix
                when * at start it will be considered a end of line filter (endswith)
                when R as first char its considered to be a regex
                everything else is a full match

        """
        others = self._children_names_get(filter=filter)
        pname = self._parent_name_get()
        if pname not in others:
            others.append(pname)
        res = [i for i in self._filter(filter=filter, llist=self._properties) if i not in others]
        return res

    def _properties_methods_names_get(self):
        properties, methods = self._inspect()
        return properties + methods

    def _props_all_names(self):
        l = (
            self._children_names_get()
            + self._properties_names_get()
            + self._dataprops_names_get()
            + self._children_names_get()
            + self._methods_names_get()
        )
        return l

    def _prop_exist(self, name):
        """
        only returns in protected mode otherwise always True
        :param name:
        :return:
        """
        if self.__class__._protected:
            if name in self._names_properties_:
                return True
            if name in self._names_methods_:
                return True
            if self._children_get(filter=name):
                return True
            if name == self._parent_name_get():
                return True
            if self._children_get(filter=name):
                return True
            if self._dataprops_get(filter=name):
                return True
            if self._methods_names_get(filter=name):
                return True
            if self._properties_names_get(filter=name):
                return True
        else:
            return True

    def _children_recursive_get(self):
        res = []
        for child in self._children.values():
            res.append(child)
            res += child._children_recursive_get()
        return res

    ###################

    def __str__(self):

        out = "## {GRAY}{RED}%s{BLUE} %s{RESET}\n\n" % (
            # self._objcat_name,
            self.__class__._location,
            self.__class__.__name__,
        )

        def add(name, color, items, out):
            if len(items) > 0:
                out += "{%s}### %s:\n" % (color, name)
                if len(items) < 20:
                    for item in items:
                        if name in ["data", "properties"]:
                            try:
                                out += " - %-20s : %s\n" % (item, getattr(self, item))
                            except:
                                out += " - %-20s : ERROR\n" % (item)
                        else:
                            out += " - %s\n" % item
                else:
                    out += " - ...\n"
            out += "\n"
            return out

        out = add("children", "GREEN", self._children_names_get(), out)
        out = add("properties", "YELLOW", self._properties_names_get(), out)
        out = add("data", "GRAY", self._dataprops_names_get(), out)

        out += "{RESET}"

        out = j.core.tools.text_replace(out, ignore_error=True)
        print(out)

        # TODO: *1 dirty hack, the ansi codes are not printed, need to check why
        return ""

    __repr__ = __str__
