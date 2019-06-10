import os
from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass


class SonicServer(JSConfigClient):
    _SCHEMATEXT = """
           @url =  jumpscale.sonic.server.1
           name* = "" (S)
           host = "127.0.0.1" (S)
           port = 1491 (I)
           password = "" (S)
           """

    def _init(self):
        self.config_path = j.sal.fs.joinPaths(j.dirs.CFGDIR, "sonic_config.cfg")
        self._default_client = None

    def start(self):
        """
        start sonic in tmux
        kosmos 'j.servers.sonic.start()'
        """
        if not j.sal.fs.exists(self.config_path):
            config_template = j.sal.fs.joinPaths(j.sal.fs.getDirName(os.path.abspath(__file__)), "sonic_config.cfg")
            j.sal.fs.symlink(config_template, self.config_path)
        self.startupcmd.start()
        return self

    @property
    def default_client(self):
        if not self._default_client:
            self._default_client = j.clients.sonic.get(name="default", host=self.host, port=self.port,
                                                       password=self.password)
            self._default_client.save()
        return self._default_client

    def stop(self):
        self._log_info("stop sonic server")
        self.startupcmd.stop()

    @property
    def startupcmd(self):
        cmd = "sonic -c {}".format(self.config_path)
        env = {"address": "{}:{}".format(self.host, self.port), "password": self.password}
        return j.tools.startupcmd.get(name="Sonic", cmd=cmd, env=env)

    def build(self, reset=True):
        """
        kosmos 'j.servers.sonic.build()'
        """
        j.builders.apps.sonic.install(reset=reset)
