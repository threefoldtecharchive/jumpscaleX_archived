from .JSBase import JSBase
from Jumpscale import j

"""
adds test management to JSBASE
"""


class JSFactoryTools:

    #### TESTING FUNCTIONALITY

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

    def _code_run(self, path, name=None, obj_key="main", die=True, **kwargs):
        if not path.startswith("/"):
            path = self._dirpath + "/" + path
        assert j.sal.fs.exists(path)
        method = j.tools.codeloader.load(obj_key=obj_key, path=path)
        self._log_debug("##:LOAD: path: %s\n\n" % path)
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
                # self.__class__._test_runs_error[name] = e
                return e
            # self.__class__._test_runs[name] = res
        return res

    def __find_code(self, name, path="tests", recursive=True):
        if not path.startswith("/"):
            path = self._dirpath + "/" + path
        assert j.sal.fs.exists(path)
        name_test = name.split("_")[1]
        name_test = name_test.split(".")[0]
        for item in j.sal.fs.listFilesInDir(path, recursive=recursive, filter="*.py"):
            bname = j.sal.fs.getBaseName(item)
            if "_" in bname:
                bname2 = "_".join(bname.split("_", 1)[1:])  # remove part before first '_'
            else:
                bname2 = bname
            if bname2.endswith(".py"):
                bname2 = bname2[:-3]
            if bname2.strip().lower() == name_test:
                return item
        return self._test_error(name, RuntimeError("Could not find code: '%s' in %s" % (name, path)))

    def __test_run(self, name=None, obj_key="main", die=True, **kwargs):

        if name == "":
            name = None

        if name is not None:
            self._log_info("##: TEST RUN: %s" % name.upper())

        if name is not None:
            tpath = self.__find_code(name=name)
            self._code_run(name=name, path=tpath, obj_key=obj_key, die=die, **kwargs)
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
