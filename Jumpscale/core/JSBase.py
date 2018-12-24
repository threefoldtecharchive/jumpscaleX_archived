from Jumpscale import j
import inspect
import os
import copy

class JSBase:

    _dirpath_ = ""
    _logger_ = None
    _cache_expiration = 3600
    _classname = None
    _location = None
    _objid_ = None

    _test_runs = {}
    _test_runs_error = {}

    def __init__(self,init=True):
        self._cache_ = None
        if init:
            self._init()

    def _init(self):
        pass

    @property
    def _dirpath(self):
        if self.__class__._dirpath_ =="":
            self.__class__._dirpath_ = os.path.dirname(inspect.getfile(self.__class__))
        return self.__class__._dirpath_

    @property
    def __name__(self):
        if self.__class__._classname is None:
            self.__class__._classname = j.core.text.strip_to_ascii_dense(str(self.__class__))
        return self.__class__._classname

    @property
    def __location__(self):
        if self.__class__._location is None:
            if '__jslocation__' in self.__dict__:
                self.__class__._location = self.__jslocation__
            elif '__jslocation__' in self.__class__.__dict__:
                self.__class__._location = self.__class__.__jslocation__
            elif '__jscorelocation__' in self.__dict__:
                self.__class__._location = self.__jslocation__
            else:
                self.__class__._location = self.__name__.lower()
        return self.__class__._location

    @property
    def _objid(self):
        if self._objid_ is None:
            id = self.__location__
            for item in ["instance", "_instance", "_id", "id", "name", "_name"]:
                if item in self.__dict__ and self.__dict__[item]:
                    id += "_" + str(self.__dict__[item])
                    break
            self._objid_ = id
        return self._objid_

    @property
    def _logger(self):
        if self.__class__._logger_ is None:
            self.__class__._logger_ = j.logger.get(self.__location__)
            self.__class__._logger_._parent = self
        return self.__class__._logger_


    def _logger_enable(self):
        self.__class__._logger_ = None
        self._logger.level = 0

    @property
    def _cache(self):
        if self._cache_ is None:
            self._cache_ = j.core.cache.get(self._objid, expiration=self._cache_expiration)
        return self._cache_

    @property
    def _ddict(self):
        dd=copy.copy(self.__dict__)
        remove=[]
        for key,val in dd.items():
            if key.startswith("_"):
                remove.append(key)
        for item in remove:
            dd.pop(item)
        return dd


    def _warning_raise(self,msg,e=None,cat=""):
        """

        :param msg:
        :param e: the python error e.g. after try: except:
        :param cat: any dot notation
        :return:
        """
        msg="ERROR in %s\n"%self
        msg+="msg\n"
        j.shell()
        w


    def _error_bug_raise(self,msg,e=None,cat=""):
        """

        :param msg:
        :param e: the python error e.g. after try: except:
        :param cat: any dot notation
        :return:
        """
        if cat == "":
            out = "BUG: %s"%msg
        else:
            out = "BUG (%s): %s "%(cat,msg)
        out+=msg+"\n"
        raise RuntimeError(msg)


    def _error_input_raise(self,msg,cat=""):
        if cat == "":
            msg = "ERROR_INPUT: %s"%msg
        else:
            msg = "ERROR_INPUT (%s): %s "%(cat,msg)
        j.shell()
        print()
        sys.exit(1)

    def _error_monitor_raise(self,msg,cat=""):
        if cat == "":
            msg = "ERROR_MONITOR: %s"%msg
        else:
            msg = "ERROR_MONITOR (%s): %s "%(cat,msg)
        j.shell()
        print()
        sys.exit(1)

    def _test_error(self, name, error):
        j.errorhandler.try_except_error_process(error, die=False)
        self.__class__._test_runs_error[name] = error

    def _test_run(self, name="", obj_key="main", **kwargs):
        """

        :param name: name of file to execute can be e.g. 10_test_my.py or 10_test_my or subtests/test1.py
                    the tests are found in subdir tests of this file

                if empty then will use all files sorted in tests subdir, but will not go in subdirs

        :param obj_key: is the name of the function we will look for to execute, cannot have arguments
               to pass arguments to the example script, use the templating feature, std = main

    def _done_set(self,name="",value=True):
        if name!="":
            return j.core.db.hset("done",self._objid,value)
        else:
            return j.core.db.hset("done","%s:%s"%(self._objid,name),value)

    def _done_get(self,name=""):
        if name!="":
            return j.core.db.hget("done",self._objid)
        else:
            return j.core.db.hget("done","%s:%s"%(self._objid,name))

    def _done_reset(self,name=""):
        """
        if name =="" then will remove all from this object
        :param name:
        :return:
        """
        if name!="":
            for item in  j.core.db.hkeys("done","%s*"%self._objid):
                 j.core.db.hdel("done",item)
        else:
            return j.core.db.hdel("done","%s:%s"%(self._objid,name))


    def __str__(self):
        try:
            out = "%s\n%s\n"%(self.__class__,str(j.data.serializers.yaml.dumps(self._ddict)))
        except:
            out = str(self.__class__)+"\n"
            out+=j.core.text.prefix(" - ", str(self.__dict__))
        return out

    __repr__ = __str__
