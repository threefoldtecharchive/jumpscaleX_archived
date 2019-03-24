from .StartupCMD import StartupCMD
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class StartupCMDFactory(j.application.JSBaseClass):

    def __init__(self):
        self.__jslocation__ = "j.data.startupcmd"
        JSBASE.__init__(self)

        tdir = j.sal.fs.joinPaths(j.sal.fs.joinPaths(j.dirs.VARDIR, "cmds"))
        j.sal.fs.createDir(tdir)

        self._cmdsdir = tdir

        self.StartupCMDClass = StartupCMD

    def get(self, name, cmd, path="", timeout=30):  # TODO:*1 better get
        return self.StartupCMDClass(cmd_start=cmd, path=path, name=name, timeout=timeout)

    def test(self):
        """
        kosmos 'j.data.startupcmd.test()'
        :return:
        """

        startup_object = j.data.startupcmd.StartupCMDClass()

        startup_object.name = "test"

        assert startup_object.data.name == "test"

        startup_mc = self.get("mc_process", "mc", path="/tmp", timeout=10)

        assert startup_mc.data.name == "mc_process"
        assert startup_mc.data.path == "/tmp"
        assert startup_mc.data.cmd_start == "mc"
        assert startup_mc.data.timeout == 10
        assert startup_mc.name == "mc_process"
        assert startup_mc.path == "/tmp"
        assert startup_mc.cmd_start == "mc"
        assert startup_mc.timeout == 10

        self._log_info("start process mc")
        startup_mc.start()
        assert startup_mc.running

        self._log_info("process id {}".format(startup_mc.pid))

        self._log_info("stop process mc")
        startup_mc.stop()
        assert startup_mc.running is False
