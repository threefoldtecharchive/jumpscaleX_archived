from Jumpscale import j


class BuilderCaddyFilemanager(j.builder.system._BaseClass):
    NAME = 'filemanager'
    PLUGINS = ['iyo', 'filemanager']

    def _init(self):
        self.go_runtime = j.builder.runtimes.golang
        self.templates_dir = self.tools.joinpaths(
            j.sal.fs.getDirName(__file__), 'templates')
        self.bins = [self.tools.joinpaths(self.go_runtime.go_path_bin, 'caddy')]
        self.new_dirs = ['/var/log', 'filemanager/files']
        self.dirs = {
            self.tools.joinpaths(self.templates_dir, 'filemanager_caddyfile'): 'cfg/filemanager',
        }
        self.startup = j.sal.fs.readFile(
            j.sal.fs.joinPaths(self.templates_dir, 'filemanager_startup.toml'))
        self.root_dirs = {
            '/etc/ssl/certs': '/etc/ssl/certs'
        }

    def build(self, reset=False):
        """
        build caddy with iyo authentication and filemanager plugins

        :param reset: reset the build process, defaults to False
        :type reset: bool, optional
        """
        j.builder.web.caddy.build(plugins=self.PLUGINS, reset=reset)

    def install(self, reset=False):
        """
        install caddy binary

        :param reset: reset build and installation, defaults to False
        :type reset: bool, optional
        """
        j.builder.web.caddy.install(reset=reset)
