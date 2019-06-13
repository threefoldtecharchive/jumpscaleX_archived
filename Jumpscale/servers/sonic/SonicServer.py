import os
from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass


class SonicServer(JSConfigClient):
    _SCHEMATEXT = """
           @url =  jumpscale.sonic.server.1
           name* = "default" (S)
           host = "127.0.0.1" (S)
           port = 1491 (I)
           password = "123456" (S)
           timeout = 300
           """

    def _init(self):
        self.config_path = j.sal.fs.joinPaths(j.dirs.CFGDIR, "sonic_config.cfg")
        self._default_client = None

    def start(self):
        """
        Starts sonic server in tmux
        """
        self._write_config()
        self.startupcmd.start()

    def _write_config(self):
        def do():
            cfg_template = j.sal.fs.joinPaths(j.sal.fs.getDirName(os.path.abspath(__file__)), "sonic_config.cfg")
            args = {"host": self.host, "port": self.port, "password": self.password, "timeout": self.timeout}
            j.tools.jinja2.file_render(path=cfg_template, dest=self.config_path, **args)
            return self.config_path

        return self._cache.get("sonic_{}_{}_{}".format(self.name, self.host, self.port), method=do, expire=3600)

    @property
    def default_client(self):
        if not self._default_client:
            self._default_client = j.clients.sonic.get(
                name="default", host=self.host, port=self.port, password=self.password
            )
            self._default_client.save()
        return self._default_client

    def stop(self):
        self._log_info("stop sonic server")
        self.startupcmd.stop()

    @property
    def startupcmd(self):
        cmd = "sonic -c {}".format(self.config_path)
        return j.tools.startupcmd.get(name="Sonic", cmd=cmd)

    def build(self, reset=True):
        """
        kosmos 'j.servers.sonic.build()'
        """
        j.builders.apps.sonic.install(reset=reset)
