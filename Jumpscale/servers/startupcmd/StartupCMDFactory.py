from .StartupCMD import StartupCMD

from Jumpscale import j
import time


class StartupCMDFactory(j.application.JSBaseConfigsClass):

    _CHILDCLASS = StartupCMD
    __jslocation__ = "j.servers.startupcmd"

    def _init(self):
        tdir = j.sal.fs.joinPaths(j.sal.fs.joinPaths(j.dirs.VARDIR, "cmds"))
        j.sal.fs.createDir(tdir)

        self._cmdsdir = tdir

    def test(self):
        """
        kosmos 'j.servers.startupcmd.test()'
        :return:
        """

        def http_tmux():
            self.http.delete()
            self.http.cmd_start = "python3 -m http.server"  # starts on port 8000
            self.http.ports = 8000
            self.http.start()
            assert self.http.is_running()
            self.http.stop()
            self.http.delete()

        def http_back():
            self.http.delete()
            assert startup_cmd.is_running() == False
            self.http.cmd_start = "python3 -m http.server"  # starts on port 8000
            self.http.ports = 8000
            self.http.executor = "background"
            self.http.start()
            assert startup_cmd.is_running() == True
            self.http.stop()
            assert startup_cmd.is_running() == False
            self.http.delete()

        def http_corex():
            # make sure corex is there
            j.servers.corex.default.check()
            corex = j.servers.corex.default.client

            self.http.executor = "corex"
            self.http.corex_client_name = corex.name
            self.http.delete()
            self.http.cmd_start = "python3 -m http.server"  # starts on port 8000
            self.http.ports = 8000
            self.http.executor = "corex"
            self.http.corex_client_name = corex.name
            self.http.start()

            j.shell()
            self.http.stop()
            self.http.delete()

        # NOT WORKING, SOMETHING WEIRD
        # def tmux_background():
        #     startup_cmd = self.tmuxserver
        #     startup_cmd.stop()
        #     assert startup_cmd.is_running() == False
        #     startup_cmd.executor = "background"
        #     # startup_cmd.cmd_start = "tmux -f /sandbox/cfg/.tmux.conf new -s main"
        #     startup_cmd.cmd_start = "/sandbox/bin/js_mux"
        #     startup_cmd.process_strings_regex = "^%s" % cmd_start
        #     startup_cmd.timeout = 4
        #     startup_cmd.start()
        #     assert startup_cmd.is_running() == True

        http_tmux()
        http_back()
        # http_corex()

        self.http.delete()
