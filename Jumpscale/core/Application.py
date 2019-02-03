import os
# import sys
import atexit
import struct
from collections import namedtuple
import psutil
import traceback
from .BASECLASSES.JSBase import JSBase
from .BASECLASSES.JSFactoryBase import JSFactoryBase
from .BASECLASSES.JSBaseConfig import JSBaseConfig
from .BASECLASSES.JSBaseConfigs import JSBaseConfigs
from .BASECLASSES.JSBaseConfigParent import JSBaseConfigParent
import gc
import sys
import types
import time
class JSGroup():
    pass



class Application(object):

    def __init__(self,j):

        self._j = j

        self._calledexit = False

        self.state = "UNKNOWN"
        self.appname = 'UNKNOWN'

        self.logger = None

        self._debug = None

        self._systempid = None

        self.interactive = True

        self.schemas = None

        self.errors_init = []
        self._bcdb_system = None

        self._JSGroup = JSGroup

        self.appname = "unknown"

    @property
    def appname(self):
        return self._j.core.myenv.appname

    @appname.setter
    def appname(self,val):
        self._j.core.myenv.appname = val


    @property
    def bcdb_system(self):
        if self._bcdb_system is None:
            bcdb =  self._j.data.bcdb.get("system",die=False)
            if bcdb is None:
                bcdb = self._j.data.bcdb.new("system",None)
            self._bcdb_system = bcdb
        return self._bcdb_system

    def bcdb_system_configure(self,addr, port, namespace,secret):
        """
        will remember that this becdb is being used
        will remember in redis (encrypted)
        :return:
        """
        self._j.shell()

    def _trace_get(self, ttype, err, tb=None):

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

    def _check_debug(self):
        if not "JSGENERATE_DEBUG" in os.environ:
            return False
        if os.environ["JSGENERATE_DEBUG"] in ["1", "Y"]:
            return True
        return False

    def error_init(self,cat,obj,error,die=True):


        print("ERROR: %s:%s"%(cat,obj))
        print (error)
        trace = self._trace_get(ttype=None, err=error)
        self.errors_init.append((cat,obj,error,trace))
        if not self._check_debug():
                msg = "%s:%s:%s"%(cat,obj,error)
                # self.report_errors()
                raise RuntimeError(msg)
        return "%s:%s:%s"%(cat,obj,error)


    @property
    def JSBaseClass(self):
        """
        JSBASE = j.application.JSBaseClass
        class myclass(j.application.JSBaseClass):
            def __init__(self):
                JSBASE.__init__(self)

        """
        return JSBase

    @property
    def JSFactoryBaseClass(self):
        """
        JSFactoryBase = j.application.JSFactoryBaseClass
        class myclass(JSFactoryBase):
            def __init__(self):
                JSFactoryBase.__init__(self)

        """
        return JSFactoryBase

    @property
    def JSBaseConfigClass(self):
        """
        JSBase = j.application.JSBaseConfigClass
        class myclass(JSBase):
            def __init__(self):
                JSBase.__init__(self)

        """
        return JSBaseConfig

    @property
    def JSBaseConfigParentClass(self):
        """
        JSBase = j.application.JSBaseConfigParentClass
        class myclass(JSBase):
            def __init__(self):
                JSBase.__init__(self)

        """
        return JSBaseConfigParent



    @property
    def JSBaseConfigsClass(self):
        """
        JSBase = j.application.JSBaseConfigClass
        class myclass(JSBase):
            def __init__(self):
                JSBase.__init__(self)

        """
        return JSBaseConfigs




    def reset(self):
        """
        empties the core.db
        """
        if self._j.core.db is not None:
            for key in self._j.core.db.keys():
                self._j.core.db.delete(key)
        self.reload()

    def reload(self):
        self._j.tools.jsloader.generate()

    @property
    def debug(self):
        if self._debug is None:
            self._debug = self._j.core.state.configGetFromDictBool(
                "system", "debug", False)
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value

    def break_into_jshell(self, msg="DEBUG NOW"):
        if self.debug is True:
            self._log_debug(msg)
            from IPython import embed
            embed()
        else:
            raise self._j.exceptions.RuntimeError(
                "Can't break into jsshell in production mode.")

    def init(self):
        pass

    @property
    def systempid(self):
        if self._systempid is None:
            self._systempid = os.getpid()
        return self._systempid

    def start(self, name=None):
        '''Start the application

        You can only stop the application with return code 0 by calling
        self._j.application.stop(). Don't call sys.exit yourself, don't try to run
        to end-of-script, I will find you anyway!
        '''
        if name:
            self.appname = name

        if "JSPROCNAME" in os.environ:
            self.appname = os.environ["JSPROCNAME"]

        if self.state == "RUNNING":
            raise self._j.exceptions.RuntimeError(
                "Application %s already started" % self.appname)

        # Register exit handler for sys.exit and for script termination
        atexit.register(self._exithandler)
        # Set state
        self.state = "RUNNING"

        # self._log_info("***Application started***: %s" % self.appname)

    def stop(self, exitcode=0, stop=True):
        '''Stop the application cleanly using a given exitcode

        @param exitcode: Exit code to use
        @type exitcode: number
        '''
        import sys

        # TODO: should we check the status (e.g. if application wasnt started,
        # we shouldnt call this method)
        if self.state == "UNKNOWN":
            # Consider this a normal exit
            self.state = "HALTED"
            sys.exit(exitcode)

        # Since we call os._exit, the exithandler of IPython is not called.
        # We need it to save command history, and to clean up temp files used by
        # IPython itself.
        # self._log_debug("Stopping Application %s" % self.appname)
        try:
            __IPYTHON__.atexit_operations()
        except BaseException:
            pass

        self._calledexit = True
        # to remember that this is correct behavior we set this flag

        # tell gridmaster the process stopped

        # TODO: this SHOULD BE WORKING AGAIN, now processes are never removed

        if stop:
            sys.exit(exitcode)

    def _exithandler(self):
        # Abnormal exit
        # You can only come here if an application has been started, and if
        # an abnormal exit happened, i.e. somebody called sys.exit or the end of script was reached
        # Both are wrong! One should call self._j.application.stop(<exitcode>)
        # TODO: can we get the line of code which called sys.exit here?

        # self._j.logger.log("UNCLEAN EXIT OF APPLICATION, SHOULD HAVE USED self._j.application.stop()", 4)
        import sys
        if not self._calledexit:
            self.stop(stop=False)

    # def getCPUUsage(self):
    #     """
    #     try to get cpu usage, if it doesn't work will return 0
    #     By default 0 for windows
    #     """
    #     try:
    #         pid = os.getpid()
    #         if self._j.core.platformtype.myplatform.isWindows:
    #             return 0
    #         if self._j.core.platformtype.myplatform.isLinux:
    #             command = "ps -o pcpu %d | grep -E --regex=\"[0.9]\"" % pid
    #             self._log_debug("getCPUusage on linux with: %s" % command)
    #             exitcode, output, err = self._j.sal.process.execute(
    #                 command, True, False)
    #             return output
    #         elif self._j.core.platformtype.myplatform.isSolaris():
    #             command = 'ps -efo pcpu,pid |grep %d' % pid
    #             self._log_debug("getCPUusage on linux with: %s" % command)
    #             exitcode, output, err = self._j.sal.process.execute(
    #                 command, True, False)
    #             cpuUsage = output.split(' ')[1]
    #             return cpuUsage
    #     except Exception:
    #         pass
    #     return 0

    def getMemoryUsage(self):
        """
        for linux is the unique mem used for this process
        is in KB
        """
        p = psutil.Process()
        info = p.memory_full_info()
        return info.uss / 1024

    def getProcessObject(self):
        return self._j.sal.process.getMyProcessObject()
    #
    # def reload(self):
    #     # from importlib import reload
    #     from IPython.lib.deepreload import reload as dreload
    #     l=[]
    #     for name,group in self._j.core._groups.items():
    #         for key,obj in group.__dict__.items():
    #             if obj is not None:
    #                 print("GROUP_OBJ:%s"%key)
    #                 self._walk_obj(obj)
    #                 print("POP:%s"%key)
    #                 del group.__dict__[key]
    #                 group.__dict__[key]=None
    #
    #     res=[]
    #     for key,mod in sys.modules.items():
    #         s=str(mod).lower()
    #         if s.find("jumpscale")!=-1 and s.find("_init")==-1 and s.find("/core/")==-1 and s.find("jumpscale_generated")==-1:
    #             res.append(key)
    #
    #     for key in res:
    #         self._j.shell()
    #
    #         try:
    #             dreload(sys.modules[key])
    #         except:
    #             print("could not reload:%s"%key)
    #         # print("module delete:%s"%key)
    #         # del sys.modules[key]
    #         # exec("del %s"%key)
    #         # sys.modules.pop(key)



    def _walk_obj(self,obj):
        j.shell()

        _factories

        if isinstance(obj,JSFactoryBase):

            for key,obj2 in obj._children.items():
                self._walk_obj(obj2)

            print("- factory empty %s"%(obj._objid))
            obj._obj_cache_reset()

        if isinstance(obj,JSBase):
            print("- base empty %s"%(obj._objid))
            obj._obj_cache_reset()

    #
    # def _get_referents(self,obj,level=0,done=[]):
    #     if isinstance(obj, types.FunctionType) or isinstance(obj, types.MethodType):
    #         return done
    #     level+=1
    #     try:
    #         r=str(obj)
    #     except:
    #         r="unknown"
    #     r.replace("\n","")
    #     if len(r)>120:
    #         r=r[:120]
    #
    #     for item in gc.get_referents(obj):
    #         if item is not None and item not in done:
    #             done.append(item)
    #             done = self._get_referents(item,level=level,done=done)
    #     if hasattr(obj,"_obj_cache_reset"):
    #         print("%s: empty %s"%(level,r))
    #         obj._obj_cache_reset()
    #
    #     return done



    def _setWriteExitcodeOnExit(self, value):
        if not self._j.data.types.bool.check(value):
            raise TypeError
        self._writeExitcodeOnExit = value

    def _getWriteExitcodeOnExit(self):
        if not hasattr(self, '_writeExitcodeOnExit'):
            return False
        return self._writeExitcodeOnExit

    writeExitcodeOnExit = property(
        fset=_setWriteExitcodeOnExit,
        fget=_getWriteExitcodeOnExit,
        doc="Gets / sets if the exitcode has to be persisted on disk")

    def _gc_count(self):
        return len(gc.get_objects())
        # cs=gc.get_count()
        # res=0
        # for c in cs:
        #     res+=c
        # return res

    # def _test_gc(self):
    #     """
    #     js_shell 'j.application._test_gc()'
    #     :return:
    #     """
    #     j=self._j
    #     print ("nr of obj in gc at start: %s" % self._gc_count())
    #     print ("mem usage start:%s"% self.getMemoryUsage())
    #     o=j.clients.ssh.instances.kds
    #     print ("mem usage after 1 config obj:%s"% self.getMemoryUsage())
    #     print ("nr of obj before garbage collection: %s"%self._gc_count())
    #     del o
    #     o="a"
    #     self.reload()
    #     print ("mem usage after 1 config obj:%s"% self.getMemoryUsage())
    #     print ("nr of obj after garbage collection: %s"%self._gc_count())
    #
    #     self._j.shell()
    #
