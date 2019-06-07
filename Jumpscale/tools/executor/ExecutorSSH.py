from Jumpscale import j

from .ExecutorBase import ExecutorBase


class ExecutorSSH(ExecutorBase):
    def __init__(self, sshclient):

        self.sshclient = sshclient

        self._id = self.sshclient.uid
        self.type = "ssh"

        self.kosmos = self.sshclient.kosmos
        self.shell = self.sshclient.shell
        self.execute = self.sshclient.execute
        self.upload = self.sshclient.upload
        self.download = self.sshclient.download

        self.config_toml = self.sshclient.config_toml
        self.env_on_system_toml = self.sshclient.env_on_system_toml

        ExecutorBase.__init__(self)

        # self.__check_base = None

    # def executeRaw(self, cmd, die=True, showout=False):
    #     return self.sshclient.execute(cmd, die=die, showout=showout)

    # def executeRaw(self, cmds, die=True, showout=True, timeout=120):
    #     rc, out, err = self.sshclient.execute(cmds, die=die, showout=showout, timeout=timeout)
    #     return rc, out, err

    def save(self):
        self.sshclient.save()

    def __repr__(self):
        return "Executor ssh: %s (%s)" % (self.sshclient.addr, self.sshclient.port)

    __str__ = __repr__
