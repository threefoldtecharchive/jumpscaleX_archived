from Jumpscale import j
import time

JSBASE = j.application.JSBaseClass


class JSRunProcess(j.application.JSBaseClass):
    def __init__(self,name,cmd="",path=None,env={},ports=[],stopcmd=None,process_strings=[]):
        JSBASE.__init__(self)
        self.name = name
        self.cmd = cmd
        self.path = path
        self.env = env
        self.ports = ports
        self.timeout = 60
        self.stopcmd = stopcmd
        self.process_strings = process_strings
        self._logger_enable()
        self._pid = None
        j.sal.fs.createDir(j.sal.fs.joinPaths(j.dirs.TMPDIR,"jumpscale","jsrun"))
        tpath = j.sal.fs.joinPaths(j.dirs.TMPDIR,"jumpscale","jsrun",self.name+".toml")
        if self.cmd!="":
            #means we need to serialize & save
            j.data.serializers.toml.dump(tpath,self._ddict)
        else:
            self.__dict__.update(j.data.serializers.toml.load(tpath))

    def _error_raise(self,msg):
        msg="error in jsrunprocess:%s\n%s\n"%(self,msg)
        raise RuntimeError(msg)

    def stop(self):
        self._logger.warning("stop:\n%s"%self)
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
                pids = j.sal.process.getPidsByFilter(pstring)
                while pids!=[]:
                    for pid in pids:
                        self._logger.debug("warning:%s"%pid)
                        j.sal.process.kill(pid)
                    time.sleep(0.2)
                    pids = j.sal.process.getPidsByFilter(pstring)

        self.wait_stopped(die=True,onetime=False,timeout=5)

    @property
    def pid(self):
        if self._pid is None:
            pids = j.sal.process.getPidsByFilter("jsrun -f -n %s"%self.name)
            if len(pids)>1:
                self._error_raise("found more than 1 pid")
            if len(pids)==0:
                return None
            self._pid =  pids[0]
        return self._pid

    @property
    def running(self):
        if self.pid is None:
            return False
        return self.wait_running(die=False,onetime=True)

    def wait_stopped(self,die=True,onetime=False,timeout=5):
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


    def wait_running(self,die=True,onetime=False,timeout=None):
        if timeout==None:
            timeout = self.timeout
        end=j.data.time.epoch+timeout
        while onetime or j.data.time.epoch<end:
            nr=0
            for port in self.ports:
                if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost",port=port):
                    nr+=1
            if nr==len(self.ports):
                self._logger.info("IS RUNNING %s"%self.name)
                return True
            if onetime:
                break
        if die:
            self._error_raise("could not start")
        else:
            return False


    def start(self,reset=False,port=None):

        if reset:
            self.stop()
        else:
            if self.running:
                self._logger.info("no need to start was already started:%s"%self.name)
                return

        self._pid = None

        tpath = j.sal.fs.joinPaths(j.dirs.TMPDIR,"jumpscale","jsrun",self.name+".sh")

        # cmd="#!sh\n"
        cmd="set +ex\n"
        for key,val in self.env.items():
            val=str(val)
            val.strip().strip('\'').strip('\"').strip('`').strip()
            cmd+="export %s=\"%s\"\n"%(key,val)
        if self.path:
            cmd+="cd %s\n"%self.path
        cmd+="%s\n"%self.cmd

        self._logger.debug("\n%s"%cmd)


        j.sal.fs.writeFile(tpath,cmd)

        j.sal.fs.chmod(tpath,0o770)

        if self.tmux:
            t=j.tools.tmux.execute(cmd2, session="jsrun", window=self.name, pane="main",window_reset=True)

        else:
            cmd2= "jsrun -f -n %s '%s'\n"%(self.name,tpath)
            self._logger.debug(cmd2)
            rc,out,err=j.sal.process.execute(cmd2,die=False)
            if rc>0:
                if err.find("session exists")!=-1:
                    if reset:
                        self.stop()
                        self.start(reset=False)
                    else:
                        #means session does already exist
                        self._error_raise("already started")
                else:
                    self._error_raise("cannot start\n%s\n%s"%(out,err))
        self.wait_running()
        assert self.running




