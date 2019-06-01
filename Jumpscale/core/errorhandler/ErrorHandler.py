import sys

from Jumpscale.core.errorhandler.JSExceptions import JSExceptions

try:
    import colored_traceback

    colored_traceback.add_hook(always=True)
except ImportError:
    pass

try:
    import pygments.lexers
    from pygments.formatters import get_formatter_by_name

    pygmentsObj = True
except BaseException:
    pygmentsObj = False

import traceback
import pudb


class ErrorHandler:
    def __init__(self, j):
        self.__jscorelocation__ = "j.tools.errorhandler"
        # JSBASE.__init__(self)
        self._j = j
        self.setExceptHook()
        self.exceptions = JSExceptions()
        self._j.exceptions = self.exceptions
        self.redis = False
        self.exit_on_error = True

    def setExceptHook(self):
        sys.excepthook = self.excepthook
        self.inException = False

    def try_except_error_process(self, err, die=True):
        """
        how to use

        try:
            ##do something
        except Exception,e:
            j.errorhandler.try_except_error_process(e,die=False) #if you want to continue

        """

        ttype, msg, tb = sys.exc_info()
        self.excepthook(ttype, err, tb, die=die)

    def _error_process(self, err, tb_text=""):
        # self._j.shell()
        if self._j.application.schemas:
            self._j.tools.alerthandler.log(err, tb_text=tb_text)
        return err

    def excepthook(self, ttype, err, tb, die=True):
        """ every fatal error in jumpscale or by python itself will result in an exception
        in this function the exception is caught.
        @ttype : is the description of the error
        @tb : can be a python data object or a Event
        """

        # print ("jumpscale EXCEPTIONHOOK")
        if self.inException:
            print("**ERROR IN EXCEPTION HANDLING ROUTINES, which causes recursive errorhandling behavior.**")
            print(err)
            sys.exit(1)
            return

        self._j.core.tools.log(msg=err, tb=tb, level=40)
        if die:
            if self._j.core.myenv.debug:
                pudb.post_mortem(tb)
            self._j.core.tools.pprint("{RED}CANNOT CONTINUE{RESET}")
            sys.exit(1)
        else:
            print("WARNING IGNORE EXCEPTIONHOOK, NEED TO IMPLEMENT: #TODO:")
        #
        #
        # print(err)
        # tb_text=""
        # if "trace_do" in err.__dict__:
        #     if err.trace_do:
        #         err._trace = self._trace_get(ttype, err, tb)
        #         # err.trace_print()
        #         print(err)
        #         tb_text = err._trace
        # else:
        #     tb_text = self._trace_get(ttype, err, tb)
        #     self._trace_print(tb_text)
        #
        # self.inException = True
        # self._error_process(err, tb_text=tb_text)
        # self.inException = False
        #
        # if die:
        #     sys.exit(1)

    def _filterLocals(self, k, v):
        try:
            k = "%s" % k
            v = "%s" % v
            if k in [
                "re",
                "q",
                "jumpscale",
                "pprint",
                "qexec",
                "jshell",
                "Shell",
                "__doc__",
                "__file__",
                "__name__",
                "__package__",
                "i",
                "main",
                "page",
            ]:
                return False
            if v.find("<module") != -1:
                return False
            if v.find("IPython") != -1:
                return False
            if v.find("bpython") != -1:
                return False
            if v.find("click") != -1:
                return False
            if v.find("<built-in function") != -1:
                return False
            if v.find("jumpscale.Shell") != -1:
                return False
        except BaseException:
            return False

        return True

    def _trace_get(self, ttype, err, tb):

        tblist = traceback.format_exception(ttype, err, tb)

        ignore = ["click/core.py", "ipython", "bpython", "loghandler", "errorhandler", "importlib._bootstrap"]

        # if self._limit and len(tblist) > self._limit:
        #     tblist = tblist[-self._limit:]
        tb_text = ""
        for item in tblist:
            for ignoreitem in ignore:
                if item.find(ignoreitem) != -1:
                    item = ""
            if item != "":
                tb_text += "%s" % item
        return tb_text

    def _trace_print(self, tb_text):
        if pygmentsObj:
            # style=pygments.styles.get_style_by_name("vim")
            formatter = pygments.formatters.Terminal256Formatter()
            lexer = pygments.lexers.get_lexer_by_name("pytb", stripall=True)  # pytb
            tb_colored = pygments.highlight(tb_text, lexer, formatter)
            sys.stderr.write(tb_colored)
            # print(tb_colored)
        else:
            sys.stderr.write(tb_text)

    def bug_escalate_developer(self, errorConditionObject, tb=None):

        tracefile = ""

        def findEditorLinux():
            apps = ["code", "micro"]
            for app in apps:
                try:
                    if self._j.system.unix.checkApplicationInstalled(app):
                        editor = app
                        return editor
                except BaseException:
                    pass
            return "micro"

        if False and self._j.application.interactive:

            editor = None
            if self._j.core.platformtype.myplatform.platform_is_linux:
                # j.tools.console.echo("THIS ONLY WORKS WHEN GEDIT IS INSTALLED")
                editor = findEditorLinux()
            elif self._j.core.platformtype.myplatform.isWindows:
                editorPath = self._j.sal.fs.joinPaths(self._j.dirs.JSBASEDIR, "apps", "wscite", "scite.exe")
                if self._j.sal.fs.exists(editorPath):
                    editor = editorPath
            tracefile = errorConditionObject.log2filesystem()
            # print "EDITOR FOUND:%s" % editor
            if editor:
                # print errorConditionObject.errormessagepublic
                if tb is None:
                    try:
                        res = self._j.tools.console.askString(
                            "\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, t=getTrace)"
                        )
                    except BaseException:  # print "ERROR IN ASKSTRING TO SEE IF WE HAVE TO USE
                        # EDITOR"
                        res = "s"
                else:
                    try:
                        res = self._j.tools.console.askString(
                            "\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, t=getTrace, d=debug)"
                        )
                    except BaseException:  # print "ERROR IN ASKSTRING TO SEE IF WE HAVE TO USE
                        # EDITOR"
                        res = "s"
                if res == "t":
                    cmd = "%s '%s'" % (editor, tracefile)
                    # print "EDITORCMD: %s" %cmd
                    if editor == "less":
                        self._j.sal.process.executeWithoutPipe(cmd, die=False)
                    else:
                        result, out, err = self._j.sal.process.execute(cmd, die=False, showout=False)

                if res == "c":
                    return
                elif res == "d":
                    self._j.tools.console.echo("Starting pdb, exit by entering the command 'q'")
                    import pdb

                    pdb.post_mortem(tb)
                elif res == "s":
                    # print errorConditionObject
                    self._j.application.stop(1)
            else:
                # print errorConditionObject
                res = self._j.tools.console.askString(
                    "\nAn error has occurred. Do you want do you want to do? (s=stop, c=continue, d=debug)"
                )
                if res == "c":
                    return
                elif res == "d":
                    self._j.tools.console.echo("Starting pdb, exit by entering the command 'q'")
                    import pdb

                    pdb.post_mortem()
                elif res == "s":
                    # print eobject
                    self._j.application.stop(1)

        else:
            # print "ERROR"
            # tracefile=eobject.log2filesystem()
            # print errorConditionObject
            # j.tools.console.echo( "Tracefile in %s" % tracefile)
            self._j.application.stop(1)
