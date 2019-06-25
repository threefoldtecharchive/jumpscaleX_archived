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

    def test(self, name=""):
        """
        it's run all tests
        kosmos 'j.servers.startupcmd.test()'
        kosmos 'j.servers.startupcmd.test(name="tmux")'

        if want run specific test ( write the name of test ) e.g. j.data.startupcmd.test(name="base")
        """
        self._test_run(name=name)
