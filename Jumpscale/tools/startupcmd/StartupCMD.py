from Jumpscale import j

import time


class StartupCMD(j.application.JSBaseDataObjClass):

    _SCHEMATEXT = """
        @url = jumpscale.startupcmd.1
        name* = ""
        cmd_start = ""
        interpreter = "bash,jumpscale" (E) 
        cmd_stop = ""
        debug = False (b)
        path = ""
        env = (dict)
        ports = (li)
        timeout = 0
        process_strings = (ls)
        pid = 0
        daemon = true (b)
        """

    def _init(self):
        self._pane_ = None
        self._pid = None

    @property
    def _pane(self):
        if self._pane_ is None:
            self._pane_ = j.tools.tmux.pane_get(window=self.name, pane="main", reset=False)
        return self._pane_

    @property
    def _cmd_path(self):
        return j.sal.fs.joinPaths(j.tools.startupcmd._cmdsdir, self.name)

    def _error_raise(self, msg):
        msg = "error in jsrunprocess:%s\n%s\n" % (self, msg)
        raise RuntimeError(msg)

    @property
    def pid(self):
        if self.process is not None:
            return self.process.pid

    @property
    def process(self):
        child = self._pane.process_obj_child
        return child

    def save(self):
        tpath = self._cmd_path+".toml"
        # means we need to serialize & save
        j.data.serializers.toml.dump(tpath, self._ddict)

    def load(self):
        tpath = self._cmd_path+".toml"
        if j.sal.fs.exists(tpath):
            self.__dict__.update(j.data.serializers.toml.load(tpath))

    def stop(self):
        self._log_warning("stop:\n%s" % self.name)
        if self.cmd_stop:
            cmd = j.tools.jinja2.template_render(text=self.cmd_stop, args=self.data._ddict)
            self._log_warning("stopcmd:%s" % cmd)
            rc, out, err = j.sal.process.execute(cmd, die=False)
            time.sleep(0.2)
        if self.pid and self.pid > 0:
            self._log_info("found process to stop:%s" % self.pid)
            j.sal.process.kill(self.pid)
            time.sleep(0.2)
        if self.process_strings != []:
            for pstring in self.process_strings:
                self._log_debug("find processes to kill:%s" % pstring)
                pids = j.sal.process.getPidsByFilter(pstring)
                while pids != []:
                    for pid in pids:
                        self._log_debug("will stop process with pid: %s" % pid)
                        j.sal.process.kill(pid)
                    time.sleep(0.2)
                    pids = j.sal.process.getPidsByFilter(pstring)

        self.wait_stopped(die=True, timeout=5)

    @property
    def running(self):
        self._log_debug("running:%s" % self.name)
        if self.ports == [] and self.process is None:
            return False
        return self.wait_running(die=False, timeout=2)

    def wait_stopped(self, die=True, timeout=5):
        self._log_debug("wait_stopped:%s" % self.name)
        end = j.data.time.epoch+timeout
        while j.data.time.epoch < end:
            nr = 0
            for port in self.ports:
                if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=port) == False:
                    nr += 1
            if nr == len(self.ports):
                self._log_info("IS HALTED %s" % self.name)
                return True
        if die:
            self._error_raise("could not stop")
        else:
            return False

    def wait_running(self, die=True, timeout=10):
        if timeout is None:
            timeout = self.timeout
        end = j.data.time.epoch+timeout
        if self.ports == []:
            time.sleep(1)  # need this one or it doesn't check if it failed
        self._log_debug("wait to run:%s (timeout:%s)" % (self.name, timeout))
        while j.data.time.epoch < end:
            time.sleep(1)
            if self.ports == []:
                if self.process:
                    if self.process.status().casefold() in ['running', 'sleeping', 'idle']:
                        self._log_info("IS RUNNING %s" % self.name)
                        return True
                elif self.daemon==False:
                    return True
            else:
                nr = 0
                for port in self.ports:
                    if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=port):
                        nr += 1
                if nr == len(self.ports) and len(self.ports) > 0:
                    self._log_info("IS RUNNING %s" % self.name)
                    return True
        if die:
            self._error_raise("could not start")
        else:
            return False

    def start(self, reset=False, checkrunning=True):
        self._log_debug("start:%s" % self.name)
        if reset:
            self.stop()
            self._pane.kill()
        else:
            if self.running:
                self._log_info("no need to start was already started:%s" % self.name)
                return

        self._pid = None

        if self.interpreter=="bash":
            C = """         
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
        else:
            C = """
            from Jumpscale import j
            {% if cmdpath != None %}
            #cd {{cmdpath}}
            {% endif %}            
            {{cmd}}          
            """


        C2 = j.core.text.strip(C)
        C3 = j.tools.jinja2.template_render(text=C2, args=self.env, cmdpath=self.path,
                                            cmd=self.cmd_start, name=self.name)

        #NEED TO BE CAREFUL< THINGS WILL FAIL IF WE ENABLE AGAIN
        # if self.interpreter == "bash":
        #     # C3 = C3.replace("\"", "'").replace("''", "'")
        #     C3 = C3.replace("\"", "'")

        self._log_debug("\n%s" % C3)


        if self.interpreter=="bash":
            tpath = self._cmd_path+".sh"
        elif self.interpreter=="jumpscale":
            tpath = self._cmd_path+".py"
        else:
            raise RuntimeError("only jumpscale or bash supported")


        j.sal.fs.writeFile(tpath, C3+"\n\n")
        j.sal.fs.chmod(tpath, 0o770)

        if "__" in self._pane.name:
            self._pane.kill()

        if self.interpreter=="bash":
            self._pane.execute("source %s" % tpath)
        else:
            if self.debug:
                self._pane.execute("kosmos %s --debug" % tpath)
            else:
                self._pane.execute("kosmos %s" % tpath)

        if checkrunning:
            running = self.wait_running()
            assert self.running
