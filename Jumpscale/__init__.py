import os
import socket
import pytoml
import inspect
import sys
from importlib import util

os.environ["LC_ALL"] = "en_US.UTF-8"


def tcpPortConnectionTest(ipaddr, port, timeout=None):
    conn = None
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if timeout:
            conn.settimeout(timeout)
        try:
            conn.connect((ipaddr, port))
        except BaseException:
            return False
    finally:
        if conn:
            conn.close()
    return True


def profileStart():
    import cProfile

    pr = cProfile.Profile()
    pr.enable()
    return pr


def profileStop(pr):
    pr.disable()
    import io
    import pstats

    s = io.StringIO()
    sortby = "cumulative"
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())


# pr=profileStart()

spec = util.spec_from_file_location("IT", "/%s/core/InstallTools.py" % os.path.dirname(__file__))

from .core.InstallTools import MyEnv

MyEnv.init()

from .core.InstallTools import BaseInstaller
from .core.InstallTools import JumpscaleInstaller
from .core.InstallTools import Tools

import pudb


def my_excepthook(exception_type, exception_obj, tb):
    Tools.log(msg=exception_obj, tb=tb, level=40)
    if MyEnv.debug:
        pudb.post_mortem(tb)
    Tools.pprint("{RED}CANNOT CONTINUE{RESET}")
    sys.exit(1)


sys.excepthook = my_excepthook


class Core:
    def __init__(self, j):
        self._db = MyEnv.db
        self._dir_home = None
        self._dir_jumpscaleX = None
        self._isSandbox = None
        self._db_fakeredis = False

    @property
    def _db_fake(self):
        # print("CORE_MEMREDIS")
        import fakeredis

        self._db = fakeredis.FakeStrictRedis()
        self._db_fakeredis = True
        return self._db

    @property
    def db(self):
        if not self._db:
            # check db is already there, if not try to do again
            MyEnv.db = Tools.redis_client_get(die=False)
            self._db = MyEnv.db

            if not self._db:
                self._db = self._db_fake

        return self._db

    def db_reset(self):
        if hasattr(j.data, "cache"):
            j.data.cache._cache = {}
        self._db = None

    @property
    def dir_jumpscaleX(self):
        if self._dir_jumpscaleX is None:
            self._dir_jumpscaleX = os.path.dirname(os.path.dirname(__file__))
        return self._dir_jumpscaleX

    @property
    def isSandbox(self):
        if self._isSandbox is None:
            if self.dir_jumpscaleX.startswith("/sandbox"):
                self._isSandbox = True
            else:
                self._isSandbox = False
        return self._isSandbox


from .core.KosmosShell import *


class Jumpscale:
    def __init__(self):
        self._shell = None
        self.exceptions = None
        # Tools.j=self

    def _locals_get(self, locals_):
        def add(locals_, name, obj):
            if name not in locals_:
                locals_[name] = obj
            return locals_

        try:
            locals_ = add(locals_, "ssh", j.clients.ssh)
        except:
            pass
        try:
            locals_ = add(locals_, "iyo", j.clients.itsyouonline)
        except:
            pass

        # locals_ = add(locals_,"zos",j.kosmos.zos)

        return locals_

    def shell(self, loc=True, exit=False, locals_=None, globals_=None):

        import inspect

        KosmosShellConfig.j = self
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        f = calframe[1]
        if loc:
            print("\n*** file: %s" % f.filename)
            print("*** function: %s [linenr:%s]\n" % (f.function, f.lineno))
        from ptpython.repl import embed

        # Tools.clear()
        history_filename = "%s/.jsx_history" % MyEnv.config["DIR_HOME"]
        if not Tools.exists(history_filename):
            Tools.file_write(history_filename, "")
        # locals_= f.f_locals
        # if curframe.f_back.f_back is not None:
        #     locals_=curframe.f_back.f_back.f_locals
        # else:
        if not locals_:
            locals_ = curframe.f_back.f_locals
        locals_ = self._locals_get(locals_)
        if not globals_:
            globals_ = curframe.f_back.f_globals
        if exit:
            sys.exit(embed(globals_, locals_, configure=ptconfig, history_filename=history_filename))
        else:
            embed(globals_, locals_, configure=ptconfig, history_filename=history_filename)

    def shelli(self, loc=True, name=None, stack_depth=2):
        if self._shell == None:
            from IPython.terminal.embed import InteractiveShellEmbed

            if name is not "":
                name = "SHELL:%s" % name
            self._shell = InteractiveShellEmbed(banner1=name, exit_msg="")
        if loc:
            import inspect

            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            f = calframe[1]
            print("\n*** file: %s" % f.filename)
            print("*** function: %s [linenr:%s]\n" % (f.function, f.lineno))
        # self.clear()
        return self._shell(stack_depth=stack_depth)

    def debug(self):
        import urwid

        urwid.set_encoding("utf8")
        from ptdb import set_trace

        set_trace()


j = Jumpscale()
j.core = Core(j)
j.core._groups = {}

rootdir = os.path.dirname(os.path.abspath(__file__))
# print("- setup root directory: %s" % rootdir)


j.core.myenv = MyEnv


j.core.installer_base = BaseInstaller
j.core.installer_jumpscale = JumpscaleInstaller()
j.core.tools = Tools

j.core.profileStart = profileStart
j.core.profileStop = profileStop

# pr=profileStart()

from .core.Text import Text

j.core.text = Text(j)

from .core.Dirs import Dirs

j.dirs = Dirs(j)
j.core.dirs = j.dirs

# from .core.logging.LoggerFactory import LoggerFactory
# j.logger = LoggerFactory(j)
# j.core.logger = j.logger

from .core.Application import Application

j.application = Application(j)
j.core.application = j.application

from .core.cache.Cache import Cache

j.core.cache = Cache(j)

from .core.PlatformTypes import PlatformTypes

j.core.platformtype = PlatformTypes(j)

from .core.errorhandler.ErrorHandler import ErrorHandler

j.errorhandler = ErrorHandler(j)
j.core.errorhandler = j.errorhandler
j.exceptions = j.errorhandler.exceptions
j.core.exceptions = j.exceptions


# THIS SHOULD BE THE END OF OUR CORE, EVERYTHING AFTER THIS SHOULD BE LOADED DYNAMICALLY

j.core.application._lib_generation_path = j.core.tools.text_replace(
    "{DIR_BASE}/lib/jumpscale/Jumpscale/jumpscale_generated.py"
)

if "JSRELOAD" in os.environ and os.path.exists(j.core.application._lib_generation_path):
    print("RELOAD JUMPSCALE LIBS")
    os.remove(j.core.application._lib_generation_path)

generated = False
# print (sys.path)
if not os.path.exists(j.core.application._lib_generation_path):
    print("WARNING: GENERATION OF METADATA FOR JUMPSCALE")
    from .core.generator.JSGenerator import JSGenerator

    j.core.jsgenerator = JSGenerator(j)
    j.core.jsgenerator.generate(methods_find=True)
    j.core.jsgenerator.report()
    generated = True

ipath = j.core.tools.text_replace("{DIR_BASE}/lib/jumpscale/Jumpscale")
if ipath not in sys.path:
    sys.path.append(ipath)


import jumpscale_generated


if generated and len(j.core.application.errors_init) > 0:
    print("THERE ARE ERRORS: look in /tmp/jumpscale/ERRORS_report.md")
# else:
#     print ("INIT DONE")

# profileStop(pr)

# j.shell()

# import time
# time.sleep(1000)
