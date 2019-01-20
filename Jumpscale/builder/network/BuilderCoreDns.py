from Jumpscale import j


class BuilderCoreDns(j.builder.system._BaseClass):
    NAME = "coredns"

    def _init(self):
        self.golang = self.b.runtimes.golang
        self.package_path = j.builder.runtimes.golang.package_path_get(
            'coredns', host='github.com/coredns')

        self.bins = [j.sal.fs.joinPaths(self.package_path, 'coredns')]
        self.dirs = ['/etc/ssl/certs/']

    def build(self, reset=False):
        """
        installs and runs coredns server with redis plugin
        """
        self._init()
        if self._done_check("install", reset):
            return
        # install golang
        j.builder.runtimes.golang.install(reset=reset)
        j.builder.runtimes.golang.get('github.com/coredns/coredns', install=False, update=False)
        # go to package path and build (for coredns)
        j.builder.runtimes.golang.execute(
            'cd {} && git    add threefoldtech_coredns https://github.com/threefoldtech/coredns &&git fetch threefoldtech_coredns && git checkout threefoldtech_coredns/master && make'.format(self.package_path))

        self._done_set('install')

    def start(self, config_file=None, args=None):
        """Starts coredns with the configuration file provided

        :param config_file: config file path e.g. ~/coredns.json
        :raises j.exceptions.RuntimeError: in case config file does not exist
        :return: tmux pane
        :rtype: tmux.Pane
        """
        self._init()
        cmd = "{coredns_path}/coredns -conf {path_config}".format(
            coredns_path=self.package_path, path_config=config_file)
        j.tools.tmux.execute(window="coredns", cmd=cmd)
