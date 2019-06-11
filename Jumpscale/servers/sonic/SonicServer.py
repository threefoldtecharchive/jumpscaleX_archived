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
        """Starts sonic server in tmux

        :param host: ip to listen on (default: "0.0.0.0")
        :param port: port to listen on (default: 1491)
        :param secret: server secret (default: 123456)
        :param timeout: tcp connection timeout (default: 300)
        :return:
        """
        self.config_path = self._write_config(self.name, self.host, self.port, self.secret, self.timeout)

        self.startupcmd.start()

    def _write_config(self, name, host, port, secret, timeout):
        def do():
            config_file = j.sal.fs.joinPaths(j.core.dirs.CFGDIR, "sonic_config_{}.cfg".format(name))
            cfg_template_text = j.sal.fs.readFile(
                j.sal.fs.joinPaths(j.sal.fs.getDirName(os.path.abspath(__file__)), "sonic_config.cfg")
            )
            cfg_txt = j.core.tools.text_replace(
                cfg_template_text, {"host": host, "port": port, "secret": secret, "timeout": timeout}
            )
            j.sal.fs.writeFile(config_file, cfg_txt)
            return config_file
        return self._cache.get("sonic_config_{}_{}_{}".format(name, host, port), method=do, timeout=3600)

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
        return j.tools.startupcmd.get(name="Sonic", cmd=cmd, env=env)

    def build(self, reset=True):
        """
        kosmos 'j.servers.sonic.build()'
        """
        j.builders.apps.sonic.install(reset=reset)
