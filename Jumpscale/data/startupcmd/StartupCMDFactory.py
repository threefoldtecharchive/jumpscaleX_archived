from Jumpscale import j

JSBASE = j.application.JSBaseClass

from .StartupCMD import StartupCMD

class StartupCMDFactory(j.application.JSBaseClass):

    def __init__(self):
        self.__jslocation__ = "j.data.startupcmd"
        JSBASE.__init__(self)

        tdir = j.sal.fs.joinPaths(j.sal.fs.joinPaths(j.dirs.VARDIR,"cmds"))
        j.sal.fs.createDir(tdir)

        self._cmdsdir = tdir

        self.StartupCMDClass = StartupCMD

    def get(self,name,cmd,path=""): #TODO:*1 better get
        return self.StartupCMDClass(cmd_start=cmd,path=path,name=name)

    def test(self):
        """
        kosmos 'j.data.startupcmd.test()'
        :return:
        """

        o=j.data.startupcmd.StartupCMDClass()

        j.shell()

        o.name = "test"

        assert o.data.name == "test"

        o2 = self.get("aaa","mc",path="/tmp")

        assert o2.data.name == "aaa"
        assert o2.data.path == "/tmp"
        assert o2.data.cmd_start == "mc"
        assert o2.name == "aaa"
        assert o2.path == "/tmp"
        assert o2.cmd_start == "mc"

        o2.start()

        assert o2.running()

        j.shell()
