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

        def mc():
            startup_cmd = self.mc

            startup_cmd.path = "/tmp"
            startup_cmd.cmd_start = "mc"
            startup_cmd.timeout = 10

            self._log_info("start process mc")
            startup_cmd.start()
            assert startup_cmd.running

            self._log_info("process id {}".format(startup_cmd.pid))

            self._log_info("stop process mc")
            startup_cmd.stop()
            assert startup_cmd.running is False

            cmd = self.get(
                name="test",
                cmd_start="j.tools.console.echo('1')\nj.tools.console.echo('2')",
                interpreter="jumpscale",
                daemon=False,
            )
            cmd.start(reset=True)

        def http_tmux():
            self.http.delete()
            self.http.cmd_start = "python3 -m http.server"  # starts on port 8000
            self.http.ports = 8000
            self.http.start()
            self.http.stop()
            self.http.delete()

        def http_back():
            self.http.delete()
            self.http.cmd_start = "python3 -m http.server"  # starts on port 8000
            self.http.ports = 8000
            self.http.executor = "background"
            self.http.start()
            self.http.stop()
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

        # mc()
        # http_tmux()
        # http_back()
        http_corex()

        self.http.delete()
