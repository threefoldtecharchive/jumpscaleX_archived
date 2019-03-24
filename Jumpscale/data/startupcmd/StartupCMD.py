from Jumpscale import j

import time

class StartupCMD(j.application.JSBaseDataObjClass):

    _SCHEMATEXT ="""
        @url = jumpscale.startupcmd.1
        name* = ""
        cmd_start = ""
        cmd_stop = ""
        path = ""
        env = (dict)
        ports = (li)
        timeout = 0
        process_strings = (ls)
        pid = 0
        """

    def _init(self):
        self._pane = j.tools.tmux.pane_get(window=self.name,pane="main",reset=False)
        self._pid = None

    @property
    def _cmd_path(self):
        return j.sal.fs.joinPaths(j.data.startupcmd._cmdsdir,self.name)

    def _error_raise(self,msg):
        msg="error in jsrunprocess:%s\n%s\n"%(self,msg)
        raise RuntimeError(msg)

    @property
    def pid(self):
        if self.process is not None:
            return self.process.pid

    @property
    def process(self):
        child=self._pane.process_obj_child
        return child


    def save(self):
        j.shell()
        self.pid = None
        tdir = j.sal.fs.joinPaths(j.sal.fs.joinPaths(j.dirs.VARDIR,"tmuxcmds"))
        j.sal.fs.createDir(tdir)
        self._cmd_path = j.sal.fs.joinPaths(tdir,self.name)
        tpath = self._cmd_path+".toml"

        if self.cmd!="":
            #means we need to serialize & save
            j.data.serializers.toml.dump(tpath,self._ddict)
        else:
            self.__dict__.update(j.data.serializers.toml.load(tpath))

    def stop(self):
        self._log_warning("stop:\n%s"%self.name)
        if self.stopcmd:
            cmd = j.tools.jinja2.template_render(text=self.cmd_stop, args=self.data._ddict)
            self._log_warning("stopcmd:%s"%cmd)
            rc,out,err=j.sal.process.execute(cmd,die=False)
            time.sleep(0.2)
        if self.pid>0:
            self._log_info("found process to stop:%s"%self.pid)
            j.sal.process.kill(self.pid)
            time.sleep(0.2)
        if self.process_strings!=[]:
            for pstring in self.process_strings:
                self._log_debug("find processes to kill:%s"%pstring)
                pids = j.sal.process.getPidsByFilter(pstring)
                while pids!=[]:
                    for pid in pids:
                        self._log_debug("will stop process with pid: %s"%pid)
                        j.sal.process.kill(pid)
                    time.sleep(0.2)
                    pids = j.sal.process.getPidsByFilter(pstring)

        self.wait_stopped(die=True,onetime=False,timeout=5)


    @property
    def running(self):
        self._log_debug("running:%s"%self.name)
        if self.ports == [] and self.process is None:
            return False
        return self.wait_running(die=False,onetime=True)

    def wait_stopped(self,die=True,onetime=False,timeout=5):
        self._log_debug("wait_stopped:%s"%self.name)
        end=j.data.time.epoch+timeout
        while onetime or j.data.time.epoch<end:
            nr=0
            for port in self.ports:
                if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost",port=port)==False:
                    nr+=1
            if nr==len(self.ports):
                self._log_info("IS HALTED %s"%self.name)
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
        self._log_debug("wait to run:%s (timeout:%s,onetime:%s)"%(self.name,timeout,onetime))
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
                    self._log_info("IS RUNNING %s"%self.name)
                    return True
            if onetime:
                break
        if die:
            self._error_raise("could not start")
        else:
            return False


    def start(self,reset=False,checkrunning=True):
        self._log_debug("start:%s"%self.name)
        if reset:
            self.stop()
            self._pane.reset()
        else:
            if self.running:
                self._log_info("no need to start was already started:%s"%self.name)
                return

        self._pid = None

        C="""         
        reset
        tmux clear
        clear
        cat /sandbox/var/cmds/{{name}}.sh
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
        C3 = j.tools.jinja2.template_render(text=C2, args=self.env, cmdpath=self.path, cmd=self.cmd_start,name=self.name)
        C3 = C3.replace("\"","'").replace("''","'")
        # for key,val in self.env.items():

        self._log_debug("\n%s"%C3)

        tpath = self._cmd_path+".sh"
        j.sal.fs.writeFile(tpath,C3+"\n\n")

        j.sal.fs.chmod(tpath,0o770)

        if "__" in self._pane.name:
            self._pane.kill()
        # self._pane.name_set(self._pane.name+"__"+self.name)
        self._pane.execute("source %s"%tpath)

        if checkrunning:
            self.wait_running()
            assert self.running




