from .StartupCMD import StartupCMD
from Jumpscale import j
import time

JSBASE = j.application.JSBaseClass


class StartupCMDFactory(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.servers.startupcmd"
        JSBASE.__init__(self)

        tdir = j.sal.fs.joinPaths(j.sal.fs.joinPaths(j.dirs.VARDIR, "cmds"))
        j.sal.fs.createDir(tdir)

        self._cmdsdir = tdir

        self.StartupCMDClass = StartupCMD

    def get(
        self,
        name,
        cmd,
        cmd_stop="",
        path="/tmp",
        timeout=30,
        env={},
        ports=[],
        process_strings=[],
        interpreter="bash",
        daemon=True,
    ):
        return self.StartupCMDClass(
            cmd_start=cmd,
            path=path,
            name=name,
            timeout=timeout,
            cmd_stop=cmd_stop,
            env=env,
            ports=ports,
            process_strings=process_strings,
            interpreter=interpreter,
            daemon=daemon,
        )

    def test(self):
        """
        kosmos 'j.servers.startupcmd.test()'
        :return:
        """

        startup_object = j.servers.startupcmd.StartupCMDClass()

        startup_object.name = "test"

        assert startup_object.data.name == "test"

        startup_cmd = j.servers.startupcmd.get("mc_process", "mc", path="/tmp", timeout=10)

        assert startup_cmd.data.name == "mc_process"
        assert startup_cmd.data.path == "/tmp"
        assert startup_cmd.data.cmd_start == "mc"
        assert startup_cmd.data.timeout == 10
        assert startup_cmd.name == "mc_process"
        assert startup_cmd.path == "/tmp"
        assert startup_cmd.cmd_start == "mc"
        assert startup_cmd.timeout == 10

        self._log_info("start process mc")
        startup_cmd.start()
        assert startup_cmd.running

        self._log_info("process id {}".format(startup_cmd.pid))

        self._log_info("stop process mc")
        startup_cmd.stop()
        assert startup_cmd.running is False

        cmd = self.get(
            "test", cmd="j.tools.console.echo('1')\nj.tools.console.echo('2')", interpreter="jumpscale", daemon=False
        )
        cmd.start(reset=True)

        # time.sleep(2)
        #
        # out=cmd._pane.out_get()
        #
        # assert out.find("\n1\n2\n") != -1  #needs to be there
