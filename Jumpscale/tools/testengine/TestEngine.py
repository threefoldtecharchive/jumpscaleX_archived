import sys
from Jumpscale import j
import imp
import time
import unittest
# import new
from io import BytesIO

JSBASE = j.application.JSBaseClass


class Tee(JSBASE):

    def __init__(self, *fobjs):
        self.fileobjs = fobjs
        JSBASE.__init__(self)

    def write(self, data):
        for fileobj in self.fileobjs:
            fileobj.write(data)

    def flush(self):
        for fileobj in self.fileobjs:
            fileobj.flush()


PRINTSTR = "\r%s %s"


class TestResult(unittest.result.TestResult, JSBASE):

    def __init__(self, debug=False):
        super(TestResult, self).__init__()
        JSBASE.__init__(self)
        self.tests = dict()
        self.errors = dict()
        self.failure = dict()
        self.skipped = dict()
        self._debug = debug
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

    def startTest(self, test):
        buffer = BytesIO()
        self.tests[test] = buffer
        if self._debug:
            sys.stdout = Tee(self._original_stdout, buffer)
            sys.stderr = Tee(self._original_stderr, buffer)
        else:
            sys.stdout = buffer
            sys.stderr = buffer

    def printStatus(self, test, state=None):
        self._logger.debug(test)
        if state:
            self._logger.debug((PRINTSTR % (state, test._testMethodName)))
        else:
            self._logger.debug((PRINTSTR % (' ', test._testMethodName)))
        sys.stdout.flush()

    def addSkip(self, test, reason):
        self._restore()
        self.printStatus(test, 'S')
        self.skipped[test] = reason

    def addFailure(self, test, err):
        self._restore()
        self.printStatus(test, 'F')
        self.failure[test] = err
        self._checkDebug(test, err)

    def _checkDebug(self, test, err):
        if self._debug:
            if test in self.tests:
                self._logger.debug((self.tests[test].getvalue()))
                self._logger.debug(
                    (j.errorhandler.parsePythonExceptionObject(
                        err[1], err[2])))
            j.application.stop(1)

    def addError(self, test, err):
        self._restore()
        self.printStatus(test, 'E')
        self.errors[test] = err
        self._checkDebug(test, err)

    def addSuccess(self, test):
        self._restore()
        self.printStatus(test, "\u2713")

    def stopTest(self, test):
        self._restore()

    def _restore(self):
        sys.stderr = self._original_stdout
        sys.stdout = self._original_stdout


class Test(JSBASE):

    def __init__(self, db, testmodule):
        self.db = db
        self.testmodule = testmodule
        self.eco = None
        JSBASE.__init__(self)

    def execute(self, testrunname, debug=False):
        self._logger.debug(
            ("\n##TEST:%s %s" %
             (self.db.organization, self.db.name)))
        res = {'total': 0, 'error': 0, 'success': 0, 'failed': 0}
        self.db.starttime = time.time()
        self.db.state = 'OK'
        result = TestResult(debug)
        suite = unittest.defaultTestLoader.loadTestsFromModule(self.testmodule)
        suite.run(result)
        for test, buffer in list(result.tests.items()):
            res['total'] += 1
            name = test._testMethodName[5:]
            self.db.output[name] = buffer.getvalue()
            if test in result.errors or test in result.failure:
                if test in result.errors:
                    res['error'] += 1
                    error = result.errors[test]
                    self.db.teststates[name] = 'ERROR'
                    self.db.state = 'ERROR'
                else:
                    res['failed'] += 1
                    error = result.failure[test]
                    self.db.teststates[name] = 'FAILURE'
                    if self.db.state != 'ERROR':
                        self.db.state == 'FAILURE'
                with j.logger.nostdout():
                    eco = j.errorhandler.parsePythonExceptionObject(
                        error[1], error[2])
                    eco.tags = "testrunner testrun:%s org:%s testgroup:%s testname:%s testpath:%s" % (
                        self.db.testrun, self.db.organization, self.db.name, name, self.db.path)
                    eco.process()
                    self.db.result[name] = eco.guid
                self._logger.debug(("Fail in test %s" % name))
                self._logger.debug((self.db.output[name]))
                self._logger.debug(eco)
            else:
                res['success'] += 1
                self.db.teststates[name] = 'OK'
            pass
        self.db.endtime = time.time()
        self._logger.debug('')
        return res

    def __str__(self):
        out = ""
        for key, val in list(self.db.__dict__.items()):
            if key[0] != "_" and key not in ["source", "output"]:
                out += "%-35s :  %s\n" % (key, val)
        items = sorted(out.split("\n"))
        return "\n".join(items)

    __repr__ = __str__


class FakeTestObj(JSBASE):

    def __init__(self):
        self.source = dict()
        self.output = dict()
        self.teststates = dict()
        self.result = dict()
        JSBASE.__init__(self)


class TestEngine(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.tools.testengine"
        JSBASE.__init__(self)
        self.paths = []
        self.tests = []
        self.outputpath = "%s/apps/gridportal/base/Tests/TestRuns/" % j.dirs.BASEDIR

    # TODO: implement remote osis
    def initTests(self, noOsis, osisip="127.0.0.1", login="", passwd=""):
        self.noOsis = noOsis

    def _patchTest(self, testmod):
        if hasattr(
                testmod,
                'TEST') and not isinstance(
                testmod.TEST,
                unittest.TestCase):
            testmod.TEST = new.classobj(
                'TEST', (testmod.TEST, unittest.TestCase), {})

    def runTests(self, testrunname=None, debug=False):

        if testrunname is None:
            testrunname = j.data.time.getLocalTimeHRForFilesystem()

        for path in self.paths:
            self._logger.debug(("scan dir: %s" % path))
            if j.sal.fs.isDir(path):
                for item in j.sal.fs.listFilesInDir(
                        path, filter="*__test.py", recursive=True):
                    self.testFile(testrunname, item)
            elif j.sal.fs.isFile(path):
                self.testFile(testrunname, path)

        priority = {}
        for test in self.tests:
            if test.db.priority not in priority:
                priority[test.db.priority] = []
            priority[test.db.priority].append(test)
        prio = sorted(priority.keys())
        results = list()
        for key in prio:
            for test in priority[key]:
                # now sorted
                # print test
                results.append(
                    test.execute(
                        testrunname=testrunname,
                        debug=debug))
                if not self.noOsis:
                    guid, change, new = self.osis.set(test.db)
        total = sum(x['total'] for x in results)
        error = sum(x['error'] for x in results)
        failed = sum(x['failed'] for x in results)
        self._logger.debug(("Ran %s tests" % total))
        if error:
            self._logger.error(('%s Error' % error))
        if failed:
            self._logger.debug(('%s Failed' % failed))
        self._logger.debug('')

    def testFile(self, testrunname, filepath):
        if self.noOsis:
            testdb = FakeTestObj()
        else:
            testdb = self.osis.new()

        name = j.sal.fs.getBaseName(filepath).replace("__test.py", "").lower()
        testmod = imp.load_source(name, filepath)
        self._patchTest(testmod)

        if not hasattr(testmod, 'enable') or not testmod.enable:
            return

        test = Test(testdb, testmod)

        test.db.author = testmod.author
        test.db.descr = testmod.descr.strip()
        test.db.organization = testmod.organization
        test.db.version = testmod.version
        test.db.categories = testmod.category.split(",")
        test.db.enable = testmod.enable
        test.db.license = testmod.license
        test.db.priority = testmod.priority
        test.db.state = 'INIT'
        test.db.teststates = dict()
        test.db.testrun = testrunname
        test.db.name = name
        test.db.path = filepath
        test.db.priority = testmod.priority
        test.db.id = 0

        C = j.sal.fs.readFile(filepath)
        methods = j.data.regex.extractBlocks(C, ["def test"])
        for method in methods:
            methodname = method.split(
                "\n")[0][len("    def test_"):].split("(")[0]
            methodsource = "\n".join([item.strip()
                                      for item in method.split("\n")[1:]
                                      if item.strip() != ""])
            test.db.source[methodname] = methodsource

        if not self.noOsis:
            guid, _, _ = self.osis.set(test.db)
            test.db = self.osis.get(guid)
        self.tests.append(test)
