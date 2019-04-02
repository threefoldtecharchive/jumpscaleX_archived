from Jumpscale import j
import os
# import copy
# import sys
import inspect
import types

class JSBase:

    def __init__(self, parent=None, topclass=True,**kwargs):
        """
        :param parent: parent is object calling us
        :param topclass: if True means no-one inherits from us
        """
        self._parent = parent
        self._class_init()  # is needed to init class properties

        if topclass:
            self._init2(**kwargs)
            self._init()

        self._obj_cache_reset()

    def _class_init(self, topclass=True):

        if not hasattr(self.__class__, "_class_init_done"):

            # print("_class init:%s"%self.__class__.__name__)
            # only needed to execute once, needs to be done at init time, class inheritance does not exist
            self.__class__._dirpath_ = ""  # path of the directory hosting this class
            self.__class__.__objcat_name = ""

            self.__class__._cache_expiration = 3600  # expiration of the cache
            self.__class__._test_runs = {}
            self.__class__._test_runs_error = {}

            if not hasattr(self.__class__,"_name"):
                self.__class__._name = j.core.text.strip_to_ascii_dense(str(self.__class__)).split(".")[-1].lower()
            # short location name:
            if '__jslocation__' in self.__dict__:
                self.__class__._location = self.__jslocation__
            elif '__jslocation__' in self.__class__.__dict__:
                self.__class__._location = self.__class__.__jslocation__
            elif '__jscorelocation__' in self.__dict__:
                self.__class__._location = self.__jslocation__
            else:
                self.__class__._location = None
                parent = self._parent
                while parent is not None:
                    if hasattr(parent,"__jslocation__"):
                        self.__class__._location = parent.__jslocation__
                        break
                    parent = parent._parent
                if self.__class__._location is None:
                    self.__class__._location = self.__class__._name

            #walk to all parents, let them know that there are child classes
            self.__class__._class_children = []
            parent = self._parent
            while parent is not None:
                if parent.__class__ not in parent._class_children:
                    parent._class_children.append(parent.__class__)
                parent = parent._parent


            self.__class__._methods_ = []
            self.__class__._properties_ = []
            self.__class__._inspected_ = False

            # print("classinit_2:%s"%self.__class__)
            # print(self.__class__._properties_)

            self.__class__._logger_min_level = 100

            self.__class__._class_init_done = True

            self._key = "%s:%s" % (self.__class__._location,self.__class__._name)

            #lets make sure the initial loglevel gets set
            self._logger_set(children=False, parents=False)

    def _logging_enable_check(self):
        """

        check if logging should be disabled for current js location

        according to logger includes and excludes (configured)
        includes have a higher priority over excludes

        will not take minlevel into consideration, its only the excludes & includes

        :return: True if logging is enabled
        :rtype: bool
        """
        if j.core.myenv.config.get("DEBUG",False):
            return True
        self._key = self._key.lower()
        def check(checkitems):
            for finditem in checkitems:
                finditem = finditem.strip().lower()
                if finditem=="*":
                    return True
                if finditem=="":
                    continue
                if "*" in finditem:
                    if finditem[-1]=="*":
                        #means at end
                        if self._key.startswith(finditem[:-1]):
                            return True
                    elif finditem[0]=="*":
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


    def _logger_set(self,minlevel=None, children=True, parents=True):
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
            #if minlevel specified we overrule anything

            # print ("%s:loginit"%self.__class__._name)
            if minlevel is None:
                minlevel = int(j.core.myenv.config.get("LOGGER_LEVEL",15))

            if minlevel is not None or not self._logging_enable_check():

                self.__class__._logger_min_level = minlevel

                if parents:
                    parent = self._parent
                    while parent is not None:
                        parent._logger_minlevel_set(minlevel)
                        parent = parent._parent

                if children:

                    for kl in self.__class__._class_children:
                        # print("%s:minlevel:%s"%(kl,minlevel))
                        kl._logger_min_level = minlevel




    def _init(self):
        pass


    def _init2(self,**kwargs):
        """
        meant to be used by developers of the base classes
        :return:
        """
        self._obj_cache_reset()
        self._key = "%s:%s" % (self.__class__._location,self.__class__._name) #needs to be done 2, first in class init


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
        return self.__class__._dirpath_


    @property
    def _objid(self):
        if self._objid_ is None:
            id = self.__class__._location
            id2 = ""
            try:
                id2 = self.data.name
            except:
                pass
            if id2 == "":
                try:
                    if self.data.id is not None:
                        id2 = self.data.id
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

    def _inspect(self):
        if not self.__class__._inspected_:
            # print("INSPECT:%s"%self.__class__)
            assert self.__class__._methods_ == []
            assert self.__class__._properties_ == []
            for name, obj in inspect.getmembers(self.__class__):
                if inspect.ismethod(obj):
                    self.__class__._methods_.append(name)
                # elif name.startswith("_"):
                #     continue
                elif inspect.ismethoddescriptor(obj):
                    continue
                elif inspect.isfunction(obj):
                    self.__class__._methods_.append(name)
                elif inspect.isclass(obj):
                    self.__class__._properties_.append(name)
                elif inspect.isgetsetdescriptor(obj):
                    continue
                else:
                    self.__class__._properties_.append(name)

            for item in self.__dict__.keys():
                if item.startswith("_"):
                    continue
                if item not in self._methods_:
                    self.__class__._properties_.append(item)

            self.__class__._inspected_ = True
        # else:
        #     print("not inspect:%s"%self.__class__)

    def _properties(self,prefix=""):
        self._inspect()

        if prefix=="_":
            return [item for item in self.__class__._properties_ if
                    (item.startswith("_") and not item.startswith("__") and not item.endswith("_"))]
        if prefix=="":
            return [item for item in self.__class__._properties_ if not item.startswith("_")]
        else:
            return [item for item in self.__class__._properties_ if item.startswith(prefix)]

    def _methods(self,prefix=""):
        self._inspect()
        if prefix=="_":
            return [item for item in self.__class__._methods_ if
                    (item.startswith("_") and not item.startswith("__") and not item.endswith("_"))]
        if prefix=="":
            return [item for item in self.__class__._methods_ if not item.startswith("_")]
        else:
            return [item for item in self.__class__._methods_ if item.startswith(prefix)]

    def _properties_children(self):
        return []

    def _properties_model(self):
        return []

    @property
    def _ddict(self):
        res = {}
        for key in self.__dict__.keys():
            if not key.startswith("_"):
                v = self.__dict__[key]
                if not isinstance(v, types.MethodType):
                    res[key] = v
        return res

    ################

    def _print(self,msg,cat=""):
        self._log(msg,cat=cat,level=15)

    def _log_debug(self,msg,cat="",data=None,context=None,_levelup=1):
        self._log(msg,cat=cat,level=10,data=data,context=context,_levelup=_levelup)

    def _log_info(self,msg,cat="",data=None,context=None,_levelup=1):
        self._log(msg,cat=cat,level=20,data=data,context=context,_levelup=_levelup)

    def _log_warning(self,msg,cat="",data=None,context=None,_levelup=1):
        self._log(msg,cat=cat,level=30,data=data,context=context,_levelup=_levelup)

    def _log_error(self,msg,cat="",data=None,context=None,_levelup=1):
        self._log(msg,cat=cat,level=40,data=data,context=context,_levelup=_levelup)

    def _log_critical(self,msg,cat="",data=None,context=None,_levelup=1):
        self._log(msg,cat=cat,level=50,data=data,context=context,_levelup=_levelup)

    def _log(self,msg,cat="",level=10,data=None,context=None,_levelup=1):
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
        if j.application.debug or self.__class__._logger_min_level-1 < level:
            #now we will log

            frame_ = inspect.currentframe().f_back
            levelup = 0
            while frame_ and levelup<_levelup:
                frame_ = frame_.f_back
                levelup+=1

            fname = frame_.f_code.co_filename.split("/")[-1]
            defname = frame_.f_code.co_name
            linenr= frame_.f_lineno

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

            logdict={}
            logdict["linenr"] = linenr
            logdict["processid"] = j.application.appname
            logdict["message"] = msg
            logdict["filepath"] = fname
            logdict["level"] = level
            if context:
                logdict["context"] = context
            else:
                logdict["context"] = self._key
            logdict["cat"] = cat

            logdict["data"] = data
            if data and isinstance(data,dict):
                # shallow copy the data to avoid changing the original data
                hidden_data = data.copy()
                if "password" in data or "secret" in data or "passwd" in data:
                    hidden_data["password"] = "***"
                logdict["data"] = hidden_data

            j.core.tools.log2stdout(logdict)

    ################

    def _done_check(self, name="", reset=False):
        if reset:
            self._done_reset(name=name)
        if name == "":
            return j.core.db.hexists("done", self._objid)
        else:
            return j.core.db.hexists("done", "%s:%s" % (self._objid, name))

    def _done_set(self, name="", value="1"):
        if name == "":
            return j.core.db.hset("done", self._objid, value)
        else:
            return j.core.db.hset("done", "%s:%s" % (self._objid, name), value)

    def _done_get(self, name=""):
        if name == "":
            return j.core.db.hget("done", self._objid)
        else:
            return j.core.db.hget("done", "%s:%s" % (self._objid, name))

    def _done_reset(self, name=""):
        """
        if name =="" then will remove all from this object
        :param name:
        :return:
        """
        if name == "":
            for item in j.core.db.hkeys("done"):
                item = item.decode()
                # print("reset todo:%s" % item)
                if item.find(self._objid) != -1:
                    j.core.db.hdel("done", item)
                    # print("reset did:%s" % item)
        else:
            return j.core.db.hdel("done", "%s:%s" % (self._objid, name))

    def _test_error(self, name, error):
        j.errorhandler.try_except_error_process(error, die=False)
        self.__class__._test_runs_error[name] = error

    def _test_run(self, name="", obj_key="main", die=True, **kwargs):
        """

        :param name: name of file to execute can be e.g. 10_test_my.py or 10_test_my or subtests/test1.py
                    the tests are found in subdir tests of this file

                if empty then will use all files sorted in tests subdir, but will not go in subdirs

        :param obj_key: is the name of the function we will look for to execute, cannot have arguments
               to pass arguments to the example script, use the templating feature, std = main


        :return: result of the tests

        """

        res = self.__test_run(name=name, obj_key=obj_key, die=die, **kwargs)
        if self.__class__._test_runs_error != {}:
            for key, e in self.__class__._test_runs_error.items():
                self._log_error("ERROR FOR TEST: %s\n%s" % (key, e))
            self._log_error("SOME TESTS DIT NOT COMPLETE SUCCESFULLY")
        else:
            self._log_info("ALL TESTS OK")
        return res

    def __test_run(self, name=None, obj_key="main", die=True, **kwargs):


        if name == '':
            name = None


        if name is not None:
            self._log_info("##: TEST RUN: %s" % name.upper())

        if name is not None:

            if name.endswith(".py"):
                name = name[:-3]

            tpath = "%s/tests/%s" % (self._dirpath, name)
            tpath = tpath.replace("//", "/")
            if not name.endswith(".py"):
                tpath += ".py"
            if not j.sal.fs.exists(tpath):
                for item in j.sal.fs.listFilesInDir("%s/tests" % self._dirpath, recursive=False, filter="*.py"):
                    bname = j.sal.fs.getBaseName(item)
                    if "_" in bname:
                        bname2 = "_".join(bname.split("_", 1)[1:])  # remove part before first '_'
                    else:
                        bname2 = bname
                    if bname2.endswith(".py"):
                        bname2 = bname2[:-3]
                    if bname2.strip().lower()==name:
                        self.__test_run(name=bname, obj_key=obj_key, **kwargs)
                        return
                return self._test_error(name, RuntimeError("Could not find, test:%s in %s/tests/" % (name, self._dirpath)))

            self._log_debug("##: path: %s\n\n" % tpath)
        else:
            items = [j.sal.fs.getBaseName(item) for item in
                     j.sal.fs.listFilesInDir("%s/tests" % self._dirpath, recursive=False, filter="*.py")]
            items.sort()
            for name in items:
                self.__test_run(name=name, obj_key=obj_key, **kwargs)

            return

        method = j.tools.codeloader.load(obj_key=obj_key, path=tpath)
        self._log_debug("##:LOAD: path: %s\n\n" % tpath)
        if die or j.application.debug:
            res = method(self=self, **kwargs)
        else:
            try:
                res = method(self=self, **kwargs)
            except Exception as e:
                if j.application.debug:
                    raise e
                else:
                    j.errorhandler.try_except_error_process(e, die=False)
                self.__class__._test_runs_error[name] = e
                return e
            self.__class__._test_runs[name] = res
        return res


    def __str__(self):


        out = "## {GRAY}%s {RED}%s{BLUE} %s{RESET}\n\n"%(self.__objcat_name,self.__class__._location,self.__class__.__name__)

        def add(name,color,items,out):
            if len(items)>0:
                out+="{%s}### %s:\n"%(color,name)
                if len(items)<20:
                    for item in items:
                        out+=" - %s\n"%item
                else:
                    out+=" - ...\n"
            out+="\n"
            return out

        out = add("children","GREEN",self._properties_children(),out)
        out = add("data","YELLOW",self._properties_model(),out)
        out = add("methods","BLUE",self._methods(),out)
        out = add("properties","GRAY",self._properties(),out)

        out+="{RESET}"


        out = j.core.tools.text_replace(out)
        print(out)

        #TODO: *1 dirty hack, the ansi codes are not printed, need to check why
        return ""



    __repr__ = __str__
