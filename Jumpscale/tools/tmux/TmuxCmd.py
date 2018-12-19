from Jumpscale import j
import time

JSBASE = j.application.JSBaseClass


class TmuxCmd(JSBASE):
    def __init__(self,name,pane_name,cmd="",path=None,env={},ports=[],stopcmd=None,process_strings=[],window_name="multi"):
        JSBASE.__init__(self)
        self.name = name
        self.pane_name = pane_name
        self.window_name = window_name
        self.cmd = cmd
        self.path = path
        self.env = env
        self.ports = ports
        self.timeout = 60
        self.stopcmd = stopcmd
        self.process_strings = process_strings
        self._logger_enable()
        self._pid = None
        tdir = j.sal.fs.joinPaths(j.sal.fs.joinPaths(j.dirs.VARDIR,"tmuxcmds"))
        j.sal.fs.createDir(tdir)
        self._cmd_path = j.sal.fs.joinPaths(tdir,self.name)
        tpath = self._cmd_path+".toml"

        if self.cmd!="":
            #means we need to serialize & save
            j.data.serializers.toml.dump(tpath,self._ddict)
        else:
            self.__dict__.update(j.data.serializers.toml.load(tpath))

        self._logger_enable()
        self._pane = j.tools.tmux.pane_get(window=window_name,pane=pane_name,reset=False)



    def _error_raise(self,msg):
        msg="error in jsrunprocess:%s\n%s\n"%(self,msg)
        raise RuntimeError(msg)

    def stop(self):
        self._logger.warning("stop:\n%s"%self.name)
        if self.stopcmd:
            cmd = j.tools.jinja2.template_render(text=self.stopcmd, args=self._ddict)
            self._logger.warning("stopcmd:%s"%cmd)
            rc,out,err=j.sal.process.execute(cmd,die=False)
            time.sleep(0.2)
        if self.pid:
            self._logger.info("found process to stop:%s"%self.pid)
            j.sal.process.kill(self.pid)
            time.sleep(0.2)
        if self.process_strings!=[]:
            for pstring in self.process_strings:
                self._logger.debug("find processes to kill:%s"%pstring)
                pids = j.sal.process.getPidsByFilter(pstring)
                while pids!=[]:
                    for pid in pids:
                        self._logger.debug("will stop process with pid: %s"%pid)
                        j.sal.process.kill(pid)
                    time.sleep(0.2)
                    pids = j.sal.process.getPidsByFilter(pstring)

        self.wait_stopped(die=True,onetime=False,timeout=5)

    @property
    def pid(self):
        if self.process is not None:
            return self.process.pid

    @property
    def process(self):
        child=self._pane.process_obj_child
        return child

    @property
    def running(self):
        self._logger.debug("running:%s"%self.name)
        if self.ports == [] and self.process is None:
            return False
        return self.wait_running(die=False,onetime=True)

    def wait_stopped(self,die=True,onetime=False,timeout=5):
        self._logger.debug("wait_stopped:%s"%self.name)
        end=j.data.time.epoch+timeout
        while onetime or j.data.time.epoch<end:
            nr=0
            for port in self.ports:
                if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost",port=port)==False:
                    nr+=1
            if nr==len(self.ports):
                self._logger.info("IS HALTED %s"%self.name)
                return True
            if onetime:
                break
        if die:
            self._error_raise("could not stop")
        else:
            return False


    def wait_running(self,die=True,onetime=False,timeout=10):
        if timeout==None:
            timeout = self.timeout
        end=j.data.time.epoch+timeout
        if self.ports == []:
            time.sleep(1) #need this one or it doesn't check if it failed
        self._logger.debug("wait to run:%s (timeout:%s,onetime:%s)"%(self.name,timeout,onetime))
        while j.data.time.epoch<end:
            if self.ports == []:
                if self.process!=None and self.process.is_running():
                    return True
                continue
            else:
                nr=0
                for port in self.ports:
                    if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost",port=port):
                        nr+=1
                if nr==len(self.ports) and len(self.ports)>0:
                    self._logger.info("IS RUNNING %s"%self.name)
                    return True
            if onetime:
                break
        if die:
            self._error_raise("could not start")
        else:
            return False


    def start(self,reset=False,checkrunning=True):
        self._logger.debug("start:%s"%self.name)
        if reset:
            self.stop()
            self._pane.reset()
        else:
            if self.running:
                self._logger.info("no need to start was already started:%s"%self.name)
                return

        self._pid = None

        C="""         
        reset
        tmux clear
        clear
        cat /sandbox/var/tmuxcmds/{{name}}.sh
        set +ex
        {% for key,val in args.items() %}
        export {{key}}='{{val}}'
        {% endfor %}
        source /sandbox/env.sh
        {% if cmdpath != None %}
        cd {{cmdpath}}
        {% endif %}
        {{cmd}} 

        """

        C2=j.core.text.strip(C)
        C3 = j.tools.jinja2.template_render(text=C2, args=self.env, cmdpath=self.path, cmd=self.cmd,name=self.name)
        C3 = C3.replace("\"","'").replace("''","'")
        # for key,val in self.env.items():

        self._logger.debug("\n%s"%C3)

        tpath = self._cmd_path+".sh"
        j.sal.fs.writeFile(tpath,C3+"\n\n")

        j.sal.fs.chmod(tpath,0o770)

        if "__" in self._pane.name:
            self._pane.kill()
        self._pane.name_set(self._pane.name+"__"+self.name)
        self._pane.execute("source %s"%tpath)
        if checkrunning:
            self.wait_running()
            assert self.running




