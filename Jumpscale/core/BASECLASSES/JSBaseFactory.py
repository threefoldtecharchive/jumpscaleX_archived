from .JSBase import JSBase


class JSBaseFactory(JSBase):
    def __init__(self, parent=None, topclass=True, **kwargs):
        self._factories = {}

        JSBase.__init__(self, parent=parent, topclass=False)

        for kl in self.__class__._CHILDCLASSES:
            obj = kl(parent=self)
            # j.shell()
            if hasattr(kl, "_name"):
                name = kl._name
            else:
                name = kl.__name__
            self.__dict__[name] = obj
            self._factories[name] = obj

        if topclass:
            self._init()
            self._init_pre(**kwargs)

    def __init_class(self):

        if not hasattr(self.__class__, "__init_class_done"):

            if hasattr(self.__class__, "_CHILDCLASS"):
                self.__class__._CHILDCLASSES = [self.__class__._CHILDCLASS]

            if not hasattr(self.__class__, "_CHILDCLASSES"):
                raise RuntimeError("need _CHILDCLASSES as class property for:%s" % self)

            # always needs to be in this order at end
            JSBase.__init_class(self)
            self.__class__.__objcat_name = "factory"

    def _obj_cache_reset(self):
        """
        make sure that all objects we remember inside are emptied
        :return:
        """
        JSBase._obj_cache_reset(self)
        for factory in self._factories.values():
            factory._obj_cache_reset()

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

        if name == "":
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
                    if bname2.strip().lower() == name:
                        self.__test_run(name=bname, obj_key=obj_key, **kwargs)
                        return
                return self._test_error(
                    name, RuntimeError("Could not find, test:%s in %s/tests/" % (name, self._dirpath))
                )

            self._log_debug("##: path: %s\n\n" % tpath)
        else:
            items = [
                j.sal.fs.getBaseName(item)
                for item in j.sal.fs.listFilesInDir("%s/tests" % self._dirpath, recursive=False, filter="*.py")
            ]
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

    __repr__ = __str__
