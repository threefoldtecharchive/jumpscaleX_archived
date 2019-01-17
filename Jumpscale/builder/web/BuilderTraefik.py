from Jumpscale import j


class BuilderTraefik(j.builder.system._BaseClass):
    NAME = 'traefik'
    VERSION = '1.7.7'  # latest
    URL = 'https://github.com/containous/traefik/releases/download/v{version}/traefik_{platform}-{arch}'

    def _init(self):
        self.go_runtime = self.b.runtimes.golang
        self.traefik_dir = self.go_runtime.package_path_get('containous/traefik')
        self.bins = [self.tools.joinpaths(j.core.dirs.BINDIR, self.NAME)]
        self.dirs = ['/etc/ssl/certs/ca-certificates.crt']

    def build(self, reset=False):
        """install traefik by getting the source from https://github.com/containous/traefik
            and building it.

        :param reset: reset installation, defaults to False
        :type reset: bool, optional
        :raises j.exceptions.RuntimeError: in case go (version 1.9+) is not installed
        """
        if self._done_get('install') and not reset:
            return

        version = tuple(map(int, self.go_runtime.version.split('.')))
        if version < (1, 9):
            raise j.exceptions.RuntimeError('%s requires go version >= 1.9')

        # get the prebuilt binary, as the building needs docker...etc
        # only check for linux for now
        arch = self.go_runtime.current_arch
        if j.core.platformtype.myplatform.isLinux:
            download_url = self.URL.format(version=self.VERSION, platform='linux', arch=arch)
        else:
            raise j.exceptions.RuntimeError('platform not supported')

        dest = self.tools.joinpaths(j.core.dirs.BINDIR, self.NAME)
        self.tools.file_download(
            download_url, dest, overwrite=False, retry=3, timeout=0)
        self.tools.file_attribs(dest, mode=0o770)

        self._done_set('install')

    def start(self, config_file=None, args=None):
        """Starts traefik with the configuration file provided

        :param config_file: config file path e.g. ~/traefik.toml
        :type config_file: str, optional
        :param args: any additional arguments to be passed to traefik
        :type args: dict, optional (e.g. {'api': '', 'api.dashboard': 'true'})
        :raises j.exceptions.RuntimeError: in case config file does not exist
        :return: tmux pane
        :rtype: tmux.Pane
        """
        cmd = self.tools.joinpaths(j.core.dirs.BINDIR, self.NAME)
        if config_file and self.tools.file_exists(config_file):
            cmd += ' --configFile=%s' % config_file

        args = args or {}
        for arg, value in args.items():
            cmd += ' --%s' % arg
            if value:
                cmd += '=%s' % value

        p = j.tools.tmux.execute(cmd, window=self.NAME, pane=self.NAME, reset=True)
        return p

    def stop(self, pid=None, sig=None):
        """Stops traefik process

        :param pid: pid of the process, if not given, will kill by name
        :type pid: long, defaults to None
        :param sig: signal, if not given, SIGKILL will be used
        :type sig: int, defaults to None
        """
        if pid:
            j.sal.process.kill(pid, sig)
        else:
            j.sal.process.killProcessByName(self.NAME, sig)

    def _test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key='test_main')
