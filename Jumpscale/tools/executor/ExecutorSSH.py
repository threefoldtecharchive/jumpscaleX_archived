from Jumpscale import j

from .ExecutorBase import ExecutorBase


class ExecutorSSH(ExecutorBase):
    def __init__(self, sshclient):

        self.sshclient = sshclient

        self._id = self.sshclient.uid

        self.kosmos = self.sshclient.kosmos
        self.shell = self.sshclient.shell
        self.execute = self.sshclient.execute
        self.upload = self.sshclient.upload
        self.download = self.sshclient.download

        ExecutorBase.__init__(self)

        self.type = "ssh"

        # self.__check_base = None

    # def executeRaw(self, cmd, die=True, showout=False):
    #     return self.sshclient.execute(cmd, die=die, showout=showout)

    # def executeRaw(self, cmds, die=True, showout=True, timeout=120):
    #     rc, out, err = self.sshclient.execute(cmds, die=die, showout=showout, timeout=timeout)
    #     return rc, out, err

    @property
    def config_toml(self):
        return self.sshclient.config_toml

    @config_toml.setter
    def config_toml(self, value):
        self.sshclient.config_toml = value

    @property
    def env_on_system_toml(self):
        return self.sshclient.env_on_system_toml

    @env_on_system_toml.setter
    def env_on_system_toml(self, value):
        self.sshclient.env_on_system_toml = value

    def config_save(self, **kwargs):
        self.sshclient.config_save(**kwargs)

    def save(self):
        self.sshclient.save()
        j.shell()

    def __repr__(self):
        return "Executor ssh: %s (%s)" % (self.sshclient.addr, self.sshclient.port)

    __str__ = __repr__
