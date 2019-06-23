from Jumpscale import j

import time


class StartupCMD(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
        @url = jumpscale.startupcmd.1
        name* = ""
        cmd_start = ""
        interpreter = "bash,jumpscale" (E)
        cmd_stop = ""
        debug = False (b)
        path = ""
        env = (dict)
        ports = (LI)
        timeout = 0
        process_strings = (ls)
        process_strings_regex = (ls)
        pid = 0
        executor = "tmux,corex,foreground,background" (E)
        daemon = true (b)
        hardkill = false (b)

        state = "init,ok,error,stopped,stopping,down,notfound" (E)
        corex_client_name = "default" (S)
        corex_id = (S)
        
        error = "" (S)
        
        time_start = (T)
        time_refresh = (T)
        time_stop = (T)

        """

    def _init(self):
        self._pane_ = None
        self._corex_local_ = None
        self._refresh_init_ = False

    def _reset(self):
        self.time_start = 0
        self.time_stop = 0
        self.pid = 0
        self.state = "init"
        self.corex_id = ""

    @property
    def _cmd_path(self):
        return j.sal.fs.joinPaths(j.servers.startupcmd._cmdsdir, self.name)

    def _error_raise(self, msg):
        msg = "error in startupcmd :%s\n%s\n" % (self, msg)
        raise RuntimeError(msg)

    def delete(self):
        self._refresh_init()
        self.stop()
        j.application.JSBaseConfigClass.delete(self)
        j.sal.fs.remove(self._cmd_path + ".cmd")
        j.sal.fs.remove(self._cmd_path + ".sh")
        j.sal.fs.remove(self._cmd_path + ".lua")
        j.sal.fs.remove(self._cmd_path + ".py")

    @property
    def process(self):
        self._refresh_init()
        if self.executor == "corex" and not self._corex_local:
            self._error_raise("cannot get process object from remote corex")

        assert self.pid != "" and self.pid > 0

        return j.sal.process.getProcessObject(self.pid)

    @property
    def logs(self):
        self._refresh_init()
        if self.executor == "background":
            self._error_raise("not supported for background")
        elif self.executor == "tmux":
            self._error_raise("not supported for background")
        if self.executor == "corex":
            r = self._corex_client._query("/process/logs", params={"id": self.corex_id}, json=False)
            return r

    def _get_processes_by_port_or_filter(self, ports=True):
        if self.executor == "corex" and not self._corex_local:
            self._error_raise("cannot get process object from remote corex")

        pids_done = []
        res = []

        if ports:
            for port in self.ports:
                p = j.sal.process.getProcessByPort(port)
                if p and p.pid:
                    res.append(p)
                    pids_done.append(p.pid)

        for pstring in self.process_strings:
            for pid in j.sal.process.getPidsByFilter(self.process_strings):
                p = j.sal.process.getProcessObject(pid)
                if p.pid not in pids_done:
                    pids_done.append(p.pid)
                    res.append(p)

        if self.process_strings_regex != []:
            for pid in j.sal.process.getPidsByFilter(regex_list=self.process_strings_regex):
                p = j.sal.process.getProcessObject(pid)
                if p.pid not in pids_done:
                    pids_done.append(p.pid)
                    res.append(p)
        # we return all processes which match
        return res

    def _kill_processes_by_port_or_filter(self):
        """
        will return all processes which match the regex of filter string
        :return:
        """
        for p in self._get_processes_by_port_or_filter():
            p.kill()

    def _softkill(self):
        if self.executor == "corex":
            if not self.corex_id:
                self._corex_clean()
                self._corex_refresh()
                if not self.corex_id:
                    raise RuntimeError("corexid cannot be empty")
            r = self._corex_client.process_stop(self.corex_id)
            return r

    def _hardkill(self, signal=9):

        if self.executor == "background":
            pass
        elif self.executor == "corex":
            if not self.corex_id:
                self._corex_clean()
                self._corex_refresh()
                if not self.corex_id:
                    raise RuntimeError("corexid cannot be empty")
            r = self._corex_client.process_kill(self.corex_id)
            return r
        elif self.executor == "tmux":
            # TMUX
            self._pane.kill()
            self._pane.window.kill()
            if [item.name for item in self._pane.window.panes] == ["main"]:
                # means we only had the main tmux window left, that one can be closed
                self._pane.mgmt.window.server.kill_server()
        self.state = "stopped"
        self.time_stop = j.data.time.epoch
        self.save()

    def _refresh_init(self):
        if not self._refresh_init_:
            if self.executor == "corex":
                self._corex_clean()
            self.refresh()
            self._refresh_init_ = True

    def refresh(self):
        self._log_info("refresh: %s" % self.name)

        self.time_refresh = j.data.time.epoch

        if not self.pid:
            return

        if self.executor == "corex":
            self._corex_refresh()

        elif self.executor == "tmux" or self.executor == "background":
            if self.is_running():
                self._notify_state("ok")
            else:
                self._notify_state("down")
        else:
            j.shell()

        if not self.pid:
            return

    # def save(self):
    #     tpath = self._cmd_path + ".data"
    #     # means we need to serialize & save
    #     v = j.data.serializers.jsxdata.dumps(self.data)
    #     bine = j.data.nacl.default.encryptSymmetric(v)
    #     j.sal.fs.writeFile(tpath, bine)
    #
    # def load(self):
    #     tpath = self._cmd_path + ".data"
    #     if j.sal.fs.exists(tpath):
    #         bine = j.sal.fs.readFile(tpath, binary=True)
    #         bin = j.data.nacl.default.decryptSymmetric(bine)
    #         data = j.data.serializers.jsxdata.loads(bin)
    #         self.data = data
    #     else:
    #         self._reset()

    def stop(self, force=True):
        self._log_warning("stop: %s" % self.name)
        self._refresh_init()

        if force or not self.state in ["stopped", "down"]:

            self._notify_state("stopping")

            if self.cmd_stop:
                cmd = j.tools.jinja2.template_render(text=self.cmd_stop, args=self.data._ddict)
                self._log_warning("stopcmd:%s" % cmd)
                rc, out, err = j.sal.process.execute(cmd, die=False)
                time.sleep(0.2)

            if self.executor == "corex":
                if not self.pid and not self.corex_id:
                    return
                self._softkill()

            if self._local:

                if self.pid and self.pid > 0:
                    self._log_info("found process to stop:%s" % self.pid)
                    try:
                        j.sal.process.kill(self.pid)
                    except:
                        pass

                self._kill_processes_by_port_or_filter()

                if not self.wait_stopped(die=False, timeout=2):
                    self._hardkill()  # will remove tmux pane
                    self.wait_stopped(die=True, timeout=4)

            else:
                # means is corex
                self._softkill()  # will trigger remote kill in nice way
                if not self.wait_stopped(die=False, timeout=2):
                    self._hardkill()  # use the underlying process manager to stop
                    self.wait_stopped(die=True, timeout=4)

    def _notify_state(self, state):
        if self.state != state:
            if state in ["down", "stopped", "stopping"]:
                self.time_stop = j.data.time.epoch
            if state in ["ok"]:
                self.time_start = j.data.time.epoch
            self.state = state
            self.save()

    def is_running(self):

        self._log_debug("running:%s" % self.name)

        if self._local and self.ports != []:
            for port in self.ports:
                if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=port) == False:
                    self._notify_state("down")
                    return False
            # can return sooner because port check is good enough
            return True

        if self.executor == "corex":
            if not self.pid and not self.corex_id:
                self._error_raise("cannot check running don't have pid or corex_id")
            self.refresh()
            j.shell()

        if self._local:
            p = self.process
            if not p.status().casefold() in ["running", "sleeping", "idle"]:
                self._notify_state("down")
                return False

        self._notify_state("ok")
        return True

    def wait_stopped(self, die=True, timeout=5):
        self._log_debug("wait_stopped:%s" % self.name)
        end = j.data.time.epoch + timeout

        while j.data.time.epoch < end:
            nr = 0
            for port in self.ports:
                if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=port) == False:
                    nr += 1
            if nr == len(self.ports):
                self._log_info("IS HALTED based on TCP %s" % self.name)
                break

            time.sleep(0.05)

        while self.state != "ok" and j.data.time.epoch < end:
            if len(self._get_processes_by_port_or_filter(ports=False)) == 0:
                self.state = "stopped"
                self.save()
                return

            time.sleep(0.2)

        if die:
            self._error_raise("could not stop")
        else:
            return False

    def wait_running(self, die=True, timeout=10):
        if timeout is None:
            timeout = self.timeout
        end = j.data.time.epoch + timeout
        if self.ports == []:
            time.sleep(0.1)  # need this one or it doesn't check if it failed
        self._log_debug("wait to run:%s (timeout:%s)" % (self.name, timeout))
        while j.data.time.epoch < end:
            if self._local:
                if self.ports == []:
                    if self.process:
                        if self.process.status().casefold() in ["running", "sleeping", "idle"]:
                            self._log_info("IS RUNNING %s" % self.name)
                            return True
                    elif self.daemon == False:
                        return True
                else:
                    nr = 0
                    for port in self.ports:
                        if j.sal.nettools.tcpPortConnectionTest(ipaddr="localhost", port=port):
                            nr += 1
                    if nr == len(self.ports) and len(self.ports) > 0:
                        self._log_info("IS RUNNING %s" % self.name)
                        return True
            else:
                r = self._corex_client.process_info_get(pid=self.pid)
                time.sleep(1)
                r = self._corex_client.process_info_get(pid=self.pid)
                if r["state"] in ["stopped", "stopping", "error"]:
                    self.error = self.logs
                    self.state = "error"
                    return False
                elif r["state"] in ["running"]:
                    return True
                else:
                    j.shell()
        if die:
            self._error_raise("could not start")
        else:
            return False

    def start(self, reset=False, checkrunning=True):
        """

        :param reset:
        :param checkrunning:
        :param foreground: means will not do in e.g. tmux
        :return:
        """
        self._refresh_init()
        self._log_debug("start:%s" % self.name)
        if self.executor == "foreground" is False:
            if reset:
                self.stop()
                self._hardkill()
            else:
                if self.is_running():
                    self._log_info("no need to start was already started:%s" % self.name)
                    return

        self._pid = None

        if self.interpreter == "bash":
            C = """            
            reset
            {% if cmdobj.executor=='tmux' %}
            tmux clear
            {% endif %}
            clear
            cat /sandbox/var/cmds/{{name}}.sh
            set +ex
            {% for key,val in args.items() %}
            export {{key}}='{{val}}'
            {% endfor %}
            . /sandbox/env.sh
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

        C3 = j.tools.jinja2.template_render(
            text=C2, args=self.env, cmdpath=self.path, cmd=self.cmd_start, name=self.name, cmdobj=self
        )

        # NEED TO BE CAREFUL< THINGS WILL FAIL IF WE ENABLE AGAIN
        # if self.interpreter == "bash":
        #     # C3 = C3.replace("\"", "'").replace("''", "'")
        #     C3 = C3.replace("\"", "'")

        self._log_debug("\n%s" % C3)

        if self.interpreter == "bash":
            tpath = self._cmd_path + ".sh"
        elif self.interpreter == "jumpscale":
            tpath = self._cmd_path + ".py"
        else:
            self._error_raise("only jumpscale or bash supported")

        j.sal.fs.writeFile(tpath, C3 + "\n\n")
        j.sal.fs.chmod(tpath, 0o770)

        if self.executor == "foreground":

            self.time_start = j.data.time.epoch

            if self.interpreter == "bash":
                j.sal.process.executeWithoutPipe("bash %s" % tpath)
            else:
                if self.debug:
                    j.sal.process.executeWithoutPipe("kosmos %s --debug" % tpath)
                else:
                    j.sal.process.executeWithoutPipe("kosmos %s" % tpath)

            # was a one time
            self.time_stop = j.data.time.epoch
            self.state = "stopped"
            self.save()

        else:
            if self.executor == "background":
                self._background_start(tpath)
            elif self.executor == "corex":
                self._corex_start(tpath)
            elif self.executor == "tmux":
                self._tmux_start(tpath)

            running = self.wait_running()
            assert running

            if self._local:
                if not self.pid or self.pid == 0:
                    ps = self._get_processes_by_port_or_filter()
                    if len(ps) != 1:
                        self._error_raise(
                            "cannot use background start, should specify ports, unixsocket or process regex to make sure only 1 process returns"
                        )
                    self.pid = ps[0].pid

                j.sal.fs.remove(tpath)
            else:
                assert self.pid and self.pid > 0

            self.time_start = j.data.time.epoch
            self.state = "ok"
            self.save()

    @property
    def _local(self):
        if self.executor != "corex":
            return True
        return self._corex_local

    ####TMUX

    @property
    def _pane(self):
        if self._pane_ is None:
            self._pane_ = j.servers.tmux.pane_get(window=self.name, pane="main", reset=False)
        return self._pane_

    def _tmux_start(self, path):

        if "__" in self._pane.name:
            self._pane.kill()

        if self.interpreter == "bash":
            self._pane.execute("source %s" % path)
        else:
            if self.debug:
                self._pane.execute("kosmos %s --debug" % path)
            else:
                self._pane.execute("kosmos %s" % path)

    ####BACKGROUND

    def _background_start(self, path):
        cmd = "nohup %s >/dev/null 2>/dev/null &" % path
        j.core.tools.execute(cmd)

    ####COREX

    @property
    def _corex_client(self):
        return j.clients.corex.get(name=self.corex_client_name)

    def _corex_start(self, path):

        if self.state == "error":
            self._error_raise("process in error:\n%s" % p)

        if self.state == "ok":
            return

        r = self._corex_client.process_start("sh %s" % path)

        self.pid = r["pid"]
        self.corex_id = r["id"]

        res = self._corex_client.process_info_get(pid=self.pid)
        assert res["pid"] == self.pid

        assert str(res["id"]) == self.corex_id

    def _corex_clean(self):
        if self.pid:
            y = self._corex_client.process_info_get(pid=self.pid)
            if y:
                assert self.pid == y["pid"]
                self.corex_id = y["id"]
            else:
                self.pid = 0
                self.state = "init"
        processlist = self._corex_client.process_list()
        for x in processlist:
            clean = False
            foundpid = False
            cmd = x["command"]
            if cmd.startswith("sh %s" % self._cmd_path):
                if x["state"] in ["stopping", "init", "crashed"]:
                    self._log_warning("found leftover", x)
                    r = self._corex_client.process_kill(x["id"])
                    j.shell()
                    clean = True
                elif x["state"] in ["running"]:
                    if not foundpid:
                        self._log_info("found process with pid:\n%s" % x)
                        self.pid = x["pid"]
                        self.corex_id = x["id"]
                        self.save()
                        foundpid = True
                    else:
                        r = self._corex_client.process_kill(x["id"])
                        clean = True
                elif x["state"] in ["stopped"]:
                    clean = True
                else:
                    j.shell()

            if cmd.strip() == "":
                self._log_info("found process with empty cmd:\n%s" % x)
                r = self._corex_client.process_kill(x["id"])
                clean = True

            if x["state"] in ["crashed"]:
                if x["error"].find("No such file") != -1:
                    r = self._corex_client.process_kill(x["id"])
                    clean = True

            if clean:
                for i in range(2):
                    r = self._corex_client.process_clean()
                    time.sleep(0.1)

    @property
    def _corex_local(self):
        if not self._corex_local_:
            self._corex_local_ = False  # FOR DEBUG
            # self._corex_local_ = self._corex_client.addr.lower() in ["localhost", "127.0.0.1"]
        return self._corex_local_

    def _corex_refresh(self):

        res = self._corex_client.process_info_get(pid=self.pid, corex_id=self.corex_id)

        def update(res, state):
            dosave = False
            if not self.data.id:
                dosave = True

            self.corex_id = res["id"]

            if self.state != state:
                self.state = state
                dosave = True

            if self.time_refresh < j.data.time.epoch - 300:
                # means we write state every 5min no matter what
                dosave = True

            if self.pid != res["pid"]:
                self.pid = res["pid"]
                dosave = True

            self.time_refresh = j.data.time.epoch

            if not self.cmd_start:
                self.cmd_start = res["command"]
                self.save()

            if dosave:
                self.save()

        if res:

            if res["state"] == "running":
                update(res, state="ok")
            elif res["state"] == "stopping":
                update(res, state="stopping")
            elif res["state"] == "stopped":
                update(res, state="stopped")
            else:
                j.shell()
        else:
            self.state = "notfound"
            self.save()
