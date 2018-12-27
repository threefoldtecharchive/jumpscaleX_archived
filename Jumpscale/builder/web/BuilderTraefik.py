from Jumpscale import j


class BuilderTraefik(j.builder.system._BaseClass):
    NAME = 'traefik'

    def _init(self):
        self.tools = j.builder.tools
        self.go_runtime = j.builder.runtimes.go
        self.traefik_dir = self.go_runtime.package_path_get('containous/traefik')

    def install(self, reset=False):
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

        self.go_runtime.get('github.com/containous/go-bindata/...')
        # ensure bindata is installed
        bindata_dir = self.go_runtime.package_path_get('containous/go-bindata')
        j.sal.process.execute('cd %s && go install' % bindata_dir)
        # clone traefik repo
        j.clients.git.pullGitRepo(
            'https://github.com/containous/traefik/',
            dest=self.traefik_dir, ssh=False, depth=1, timeout=20000)
        # generate and build
        j.sal.process.execute('cd %s && go generate && go build ./cmd/traefik' % self.traefik_dir)
        # then copy the binary to GOBIN
        self.tools.file_copy(
            self.tools.joinpaths(self.traefik_dir, self.NAME),
            self.go_runtime.go_path_bin)

        self._done_set('install')

    def start(self, config_file=None):
        """Starts traefik with the configuration file provided

        :param config_file: config file path e.g. ~/traefik.toml
        :type config_file: str, optional
        :raises j.exceptions.RuntimeError: in case config file does not exist
        :return: tmux pane
        :rtype: tmux.Pane
        """
        cmd = self.tools.joinpaths(self.go_runtime.go_path_bin, self.NAME)
        if config_file and self.tools.file_exists(config_file):
            cmd += ' --configFile=%s' % config_file
        p = j.tools.tmux.execute(cmd, window=self.NAME, pane=self.NAME, reset=True)
        return p

    def stop(self, pid=None, sig=None):
        """Stops traefik process

        :param pid: pid of the process, if not given, will kill by name
        :type pid: long, defaults to None
        :param sig: signal, if not given, SIGKILL will be used
        :param sig: int, defaults to None
        """
        if pid:
            j.sal.process.kill(pid, sig)
        else:
            j.sal.process.killProcessByName(self.NAME, sig)

    def test(self):
        """Testing the install/start/stop"""
        # stop at first (by name)
        self.stop()
        # install with reset
        self.install(reset=True)

        # try to start/stop
        tmux_pane = self.start()
        child_process = tmux_pane.process_obj_child
        if not child_process.is_running:
            raise j.exceptions.RuntimeError('Process did not start')
        self.stop(child_process.pid)

