from Jumpscale import j

import time
from .Monitors import Monitors


class StartupCMD(j.application.JSBaseConfigClass):

    _SCHEMATEXT = j.sal.fs.readFile(j.sal.fs.getDirName(__file__) + "/schema.toml")

    def _init(self):

        self._pane_ = None
        self._corex_local_ = None
        self._logger_enable()
        self._autosave = True  # means when change on one of the props will save automatically

        if self.executor == "corex":
            self._corex_clean()

        self.init()

    def _reset(self):
        self.runtime.time_start = 0
        self.runtime.time_stop = 0
        self.runtime.pid = 0
        self.runtime.state = "init"
        self.corex_id = ""

    @property
    def _cmd_path(self):
        return j.sal.fs.joinPaths(j.servers.startupcmd._cmdsdir, self.name)

    def _error_raise(self, msg):
        msg = "error in startupcmd :%s\n%s\n" % (self.name, msg)
        raise RuntimeError(msg)

    def init(self):
        # only runs one time (also runs when start called)
        p = self._process_detect()

    def delete(self):
        j.application.JSBaseConfigClass.delete(self)
        j.sal.fs.remove(self._cmd_path)
        j.sal.fs.remove(self._cmd_path + ".cmd")
        j.sal.fs.remove(self._cmd_path + ".sh")
        j.sal.fs.remove(self._cmd_path + ".lua")
        j.sal.fs.remove(self._cmd_path + ".py")

    def _process_detect(self):
        """
        only do this once at start or at init
        :return:
        """

        def notify_p(p):
            if p.status().casefold() in ["running", "sleeping", "idle"]:
                self._notify_state("running")
                if p.pid != self.runtime.pid:
                    self.runtime.pid = p.pid
                    self.save()
            else:
                self._notify_state("down")
            return p

        if self.runtime.pid:
            p = j.sal.process.getProcessObject(self.runtime.pid, die=False)
            if not p:
                self.runtime.pid = 0
            else:
                return notify_p(p)

        if self._local:
            ps = self._get_processes_by_port_or_filter()
            if len(ps) == 1:
                return notify_p(ps[0])

    def _get_processes_by_port_or_filter(self, process_filter=True, ports=True):
        if self.executor == "corex" and not self._corex_local:
            return self._error_raise("cannot get process object from remote corex")

        pids_done = []
        res = []

        if ports:
            for port in self.monitor.ports:
                p = j.sal.process.getProcessByPort(port)
                if p and p.pid:
                    res.append(p)
                    pids_done.append(p.pid)

        if process_filter:
            for pstring in self.monitor.process_strings:
                for pid in j.sal.process.getPidsByFilter(self.monitor.process_strings):
                    p = j.sal.process.getProcessObject(pid)
                    if p.pid not in pids_done:
                        pids_done.append(p.pid)
                        res.append(p)

            if self.monitor.process_strings_regex != []:
                for pid in j.sal.process.getPidsByFilter(regex_list=self.monitor.process_strings_regex):
                    p = j.sal.process.getProcessObject(pid)
                    if p.pid not in pids_done:
                        pids_done.append(p.pid)
                        res.append(p)
        # we return all processes which match
        return res

    @property
    def process(self):
        if self.executor == "corex" and not self._corex_local:
            return self._error_raise("cannot get process object from remote corex")

        if not self.runtime.pid:
            return

        return j.sal.process.getProcessObject(self.runtime.pid)

    def stdout_err_get(self):
        if self.executor == "background":
            return self._error_raise("not supported for background")
        elif self.executor == "tmux":
            return self._error_raise("not supported for background")
        if self.executor == "corex":
            r = self._corex_client._query("/process/logs", params={"id": self.corex_id}, json=False)
            return r

    def _kill_processes_by_port_or_filter(self):
        """
        will return all processes which match the regex of filter string
        :return:
        """
        for p in self._get_processes_by_port_or_filter():
            p.kill()

    def _softkill(self):
        """

        :return: True if it actually tried a softkill, otherwise False
        """
        if self.executor == "corex":
            if not self.corex_id:
                self._corex_clean()
                self._corex_refresh()
                if not self.corex_id:
                    raise RuntimeError("corexid cannot be empty")
            r = self._corex_client.process_stop(self.corex_id)
            return True
        if self._local:
            if self.cmd_stop:
                cmd = j.tools.jinja2.template_render(text=self.cmd_stop, args=self.data._ddict)
                self._log_warning("stopcmd:%s" % cmd)
                rc, out, err = j.sal.process.execute(cmd, die=False)
                return True
        return False

    def _hardkill(self, signal=9):
        """

        :param signal:
        :return: True if we know hardkill worked, otherwise False
        """

        # will try to use process manager but this only works for local
        if self._local:
            if self.runtime.pid and self.runtime.pid > 0:
                self._log_info("found process to stop:%s" % self.runtime.pid)
                p = self.process
                if p and self.runtime.state == "running":
                    p.kill()
                    time.sleep(0.2)

            self._kill_processes_by_port_or_filter()

        if self.executor == "background":
            # only process mechanism above can have worked
            return False
        elif self.executor == "corex":
            if not self.corex_id:
                self._corex_clean()
                self._corex_refresh()
                if not self.corex_id:
                    raise RuntimeError("corexid cannot be empty")
            r = self._corex_client.process_kill(self.corex_id)
            self._notify_state("stopped")
            return True
        elif self.executor == "tmux":
            # TMUX
            self._pane.kill()
            self._pane.window.kill()
            # if [item.name for item in self._pane.window.panes] == ["main"]:
            #     # means we only had the main tmux window left, that one can be closed
            #     self._pane.mgmt.window.server.kill_server()
            self._notify_state("stopped")
            return True

    def refresh(self):
        """
        refresh the state of the running process
        :return:
        """
        self._log_info("refresh: %s" % self.name)

        self.time_refresh = j.data.time.epoch

        if self.executor == "foreground":
            return

        if self.executor == "corex":
            self._corex_refresh()

        if self.is_running():
            self._notify_state("running")
        else:
            self._notify_state("down")

    def stop(self, force=False, waitstop=True, die=True):
        """

        :param force: will do a hardkill after the softkill even if it measures down
        :param die: will die if we confirmed is still alive
        :param waitstop: will wait to stop
        :return: True (was ok), -1: we don't know, False (it did not stop, only relevant if die=False)
        """
        self._log_warning("stop: %s" % self.name)

        if self.is_running() == False:  # if we don't know it will be -1
            return

        self._notify_state("stopping")

        if self._softkill():
            # means we really tried a softkill
            stopped = self.wait_stopped(die=False, timeout=self.timeout)
            if stopped == True and force == False:  # this means we really know for sure it died
                return True

        self._hardkill()  # will remove tmux pane or other hard method of stopping

        if waitstop:
            self.wait_stopped(die=die, timeout=self.timeout)
            if die:
                return True
        return -1  # we could not know for sure

    def _notify_state(self, state):
        """
        make sure we keep the state table healthy

        state = "init,running,error,stopped,stopping,down,notfound" (E)

        :param state:
        :return:
        """
        if self.runtime.state != state:
            if state in ["down", "stopped", "stopping", "notfound", "init"]:
                self.runtime.time_stop = j.data.time.epoch
            if state in ["running"]:
                self.runtime.time_start = j.data.time.epoch
            self.runtime.state = state
            self.save()

    def _is_running(self):

        # self._log_debug("running:%s" % self.name)

        nrok = 0
        res = []

        nrok_, res_ = Monitors.tcp_check(self)
        nrok += nrok_
        res += res_

        nrok_, res_ = Monitors.socket_check(self)
        nrok += nrok_
        res += res_

        nrok_, res_ = Monitors.process_check(self)
        nrok += nrok_
        res += res_

        nrok_, res_ = Monitors.nrprocess_check(self)
        nrok += nrok_
        res += res_

        return nrok, res

    def is_running(self):
        """
        :return: 1 if we don't know but prob ok, 2 if ok for sure, False if not ok
        """

        # self._log_debug("running:%s" % self.name)

        nrok, errors = self._is_running()

        if len(errors) == 0:
            if self.monitor.conclusive:
                # means if conclusive and nothing found we know its running
                if len(nrok) > 0:
                    self._notify_state("running")
                    return 2
                else:
                    # we can't know for sure because there were no tests
                    return 1
            else:
                return False
        else:
            self._notify_state("down")
            return False

    def wait_running(self, die=True, timeout=None):
        """
        :param die:
        :param timeout:
        :return: will return True if it  is running, False if it did not work, -1 if we don't know
                 if die and stopped will raise error
        """
        self._log_debug("wait_running:%s" % self.name)
        if not timeout:
            timeout = self.monitor.timeout
        end = j.data.time.epoch + timeout

        while j.data.time.epoch < end:
            nrok, errors = self._is_running()
            nr_tests = nrok + len(errors)  # total tests done

            if len(errors) == 0 and nr_tests > 0:
                # now we know for sure its ok because we did tests and all tests where ok
                if self.monitor.conclusive:
                    return True
            elif nr_tests == 0:
                # no tests done, so we know nothing, but there is nothing to test
                if self.monitor.conclusive:
                    return True
                else:
                    return -1
            # means at least 1 test failed, need to keep on waiting

            time.sleep(0.1)

        if die:
            return self._error_raise("could not define process is up, timeout")
        return -1

    def wait_stopped(self, die=True, timeout=None):
        """
        :param die:
        :param timeout:
        :return: will return True if it stopped, False if it did not work,
                -1 if we don't know 100% for sure but prob down
                 if die and stopped will raise error
        """
        self._log_debug("wait_stopped:%s" % self.name)
        if not timeout:
            timeout = self.monitor.timeout
        end = j.data.time.epoch + timeout

        # dont use conclusive check here because we can do some test, its better than nothing

        while j.data.time.epoch < end:
            nrok, errors = self._is_running()
            nr_tests = nrok + len(errors)  # total tests done

            if len(errors) > 0 and len(errors) == nr_tests:
                # now we know for sure its ok because we did test and all tests where down
                if self.monitor.conclusive:
                    return True
                else:
                    return -1  # its not conclusive but prob down
            elif len(errors) > 0:
                # at least one test failed but we don't know if it was complete but enough to exit if not conclusive
                if not self.monitor.conclusive:
                    return -1
                # need to wait for more tests because is conclusive
            elif nr_tests == 0:
                # no tests done, so we know nothing, but there is nothing to test so we can say -1
                # its never True because how can we be sure with no tests? even in conclusive mode
                return -1

            time.sleep(0.1)

        if die:
            return self._error_raise("could not define process is down")

        return False

    def start(self, reset=False):
        """

        :param reset:
        :param checkrunning:
        :param foreground: means will not do in e.g. tmux
        :return:
        """
        self._log_debug("start:%s" % self.name)

        if self.executor == "foreground" is False:
            if reset:
                self.stop()
                self._hardkill()

        if self.is_running() == True:
            self._log_info("no need to start was already started:%s" % self.name)
            return

        assert self.cmd_start

        if "\n" in self.cmd_start.strip():
            C = self.cmd_start
        elif self.interpreter == "bash":
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
        elif self.interpreter in ["direct", "python"]:
            C = self.cmd_start
        elif self.interpreter == "jumpscale":
            C = """
            from Jumpscale import j
            {% if cmdpath %}
            j.sal.fs.changeDir("{{cmdpath}}")
            {% endif %}
            {{cmd}}
            """

        C2 = j.core.text.strip(C)

        C3 = j.tools.jinja2.template_render(
            text=C2, args=self.env, cmdpath=self.path, cmd=self.cmd_start, name=self.name, cmdobj=self
        )

        self._log_debug("\n%s" % C3)

        if not self._local:
            # when not local we always have to wrap in in such a way we can execute it remotely so without file
            tpath = None
            if "\n" in C3.strip():
                # means we have to wrap it in other way
                toexec = j.data.text.bash_wrap(C3)  # need to wrap a bash script to 1 line (TODO in text module)
            else:
                toexec = C3.strip()
            if self.path:
                toexec = "mkdir -p %s;cd %s;%s" % (self.path, self.path, toexec)

        elif self.interpreter == "direct":
            # means we need to execute without file unless when script
            if "\n" in C3.strip():
                tpath = self._cmd_path
                toexec = tpath
            else:
                tpath = None  # means need to execute directly
                toexec = C3.strip()

        elif self.interpreter == "bash":
            tpath = self._cmd_path + ".sh"
            toexec = "sh %s" % tpath
        elif self.interpreter in ["jumpscale", "python"]:
            tpath = self._cmd_path + ".py"
            # toexec = "python3 %s" % tpath
            if self.debug:
                toexec = "kosmos %s --debug" % tpath
            else:
                toexec = "python3 %s" % tpath
        else:
            return self._error_raise("only jumpscale or bash supported")

        if tpath:
            j.sal.fs.writeFile(tpath, C3 + "\n\n")
            j.sal.fs.chmod(tpath, 0o770)

        self.runtime.pid = 0

        if self.executor == "foreground":
            self._notify_state("running")
            j.sal.process.executeInteractive(toexec)
        elif self.executor == "background":
            self._background_start(toexec)
        elif self.executor == "tmux":
            self._tmux_start(toexec)
        elif self.executor != "corex":
            self._corex_start(toexec)
        else:
            return self._error_raise("could not find executor:'%s'" % self.executor)

        # will see if we can find the process
        self.init()

        if self.executor == "foreground":
            self._notify_state("stopped")
        else:
            running = self.wait_running(die=True)
            assert self.runtime.pid
            assert running
            self._notify_state("running")

        # if tpath:
        #     j.sal.fs.remove(tpath)

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

        j.servers.tmux.server

        if "__" in self._pane.name:
            self._pane.kill()

        if self.interpreter == "bash":
            if path.startswith("sh "):
                path = path[3:]
                self._pane.execute("source %s" % path)
            elif path.startswith("bash "):
                path = path[5:]
                self._pane.execute("source %s" % path)
            else:
                raise RuntimeError()

        else:
            self._pane.execute(path)

    ####BACKGROUND

    def _background_start(self, path):
        cmd = "nohup %s >/dev/null 2>/dev/null &" % path
        self._log_debug(cmd)
        j.core.tools.execute(cmd)

    ####COREX

    @property
    def _corex_client(self):
        return j.clients.corex.get(name=self.corex_client_name)

    def _corex_start(self, path):

        if self.runtime.state == "error":
            return self._error_raise("process in error:\n%s" % p)

        if self.runtime.state == "running":
            return

        r = self._corex_client.process_start("sh %s" % path)

        self.runtime.pid = r["pid"]
        self.corex_id = r["id"]

        res = self._corex_client.process_info_get(pid=self.runtime.pid)
        assert res["pid"] == self.runtime.pid

        assert str(res["id"]) == self.corex_id

    def _corex_clean(self):
        if self.runtime.pid:
            y = self._corex_client.process_info_get(pid=self.runtime.pid)
            if y:
                assert self.runtime.pid == y["pid"]
                self.corex_id = y["id"]
            else:
                self.runtime.pid = 0
                self.runtime.state = "init"
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
                        self.runtime.pid = x["pid"]
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

        res = self._corex_client.process_info_get(pid=self.runtime.pid, corex_id=self.corex_id)

        def update(res, state):
            dosave = False
            if not self.data.id:
                dosave = True

            self.corex_id = res["id"]

            if self.runtime.state != state:
                self.runtime.state = state
                dosave = True

            if self.time_refresh < j.data.time.epoch - 300:
                # means we write state every 5min no matter what
                dosave = True

            if self.runtime.pid != res["pid"]:
                self.runtime.pid = res["pid"]
                dosave = True

            self.time_refresh = j.data.time.epoch

            if not self.cmd_start:
                self.cmd_start = res["command"]
                self.save()

            if dosave:
                self.save()

        if res:

            if res["state"] == "running":
                update(res, state="running")
            elif res["state"] == "stopping":
                update(res, state="stopping")
            elif res["state"] == "stopped":
                update(res, state="stopped")
            else:
                j.shell()
        else:
            self.runtime.state = "notfound"
            self.save()
