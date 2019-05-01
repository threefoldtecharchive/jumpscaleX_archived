from Jumpscale import j
builder_method = j.builder.system.builder_method


class BuilderCaddyFilemanager(j.builder.system._BaseClass):
    NAME = 'filemanager'
    PLUGINS = ['iyo', 'filemanager']

    def _init(self):
        self.go_runtime = j.builder.runtimes.golang
        self.templates_dir = self.tools.joinpaths(j.sal.fs.getDirName(__file__), 'templates')
        # self.root_dirs = {
        #     '/etc/ssl/certs': '/etc/ssl/certs'
        # }

    @builder_method()
    def build(self):
        """
        build caddy with iyo authentication and filemanager plugins

        :param reset: reset the build process, defaults to False
        :type reset: bool, optional
        """
        j.builder.web.caddy.build(plugins=self.PLUGINS)

    @builder_method()
    def install(self):
        """
        install caddy binary

        :param reset: reset build and installation, defaults to False
        :type reset: bool, optional
        """
        j.builder.web.caddy.install()

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        dest_path = self.DIR_SANDBOX
        caddy_bin_path = self.tools.joinpaths(self.go_runtime.DIR_GO_PATH_BIN, 'caddy')
        bin_dest = self.tools.joinpaths(dest_path, 'sandbox', 'bin')
        self.tools.dir_ensure(bin_dest)

        self.root_dirs = {
            '/etc/ssl/certs': '/etc/ssl/certs'
        }

        # empty dirs
        self.tools.dir_ensure(self.tools.joinpaths(dest_path, 'sandbox', 'var', 'log'))
        self.tools.dir_ensure(self.tools.joinpaths(dest_path, 'sandbox', 'filemanager', 'files'))

        # bin
        self._copy(caddy_bin_path, bin_dest)

        # caddy config
        cfg_dir = self.tools.joinpaths(dest_path, 'sandbox', 'cfg', 'filemanager')
        caddyfile = self.tools.joinpaths(self.templates_dir, 'filemanager_caddyfile')
        self._copy(caddyfile, self.tools.joinpaths(cfg_dir, 'filemanager_caddyfile'))

        # startup
        startup_file = self.tools.joinpaths(self.templates_dir, 'filemanager_startup.toml')
        file_dest = self.tools.joinpaths(dest_path, '.startup.toml')
        self._write(file_dest, self.tools.file_read(startup_file))

        # copy /etc/ssl/cert
        certs = self.tools.joinpaths(dest_path, 'etc', 'ssl', 'certs')
        self.tools.dir_ensure(certs)
        self.tools.copyTree(source='/etc/ssl/certs', dest=certs)
        if flist_create:
            print(self._flist_create(zhub_client=zhub_client))
        self._done_set('sandbox')

    def test(self):
        if not j.sal.process.checkInstalled(j.builder.web.caddy.NAME):
            j.builder.web.caddy.stop()
            j.builder.web.caddy.build(reset=True)
            j.builder.web.caddy.install()
            j.builder.web.caddy.sandbox()

        # try to start/stop
        tmux_pane = j.builder.web.caddy.start()
        tmux_process = tmux_pane.process_obj
        child_process = tmux_pane.process_obj_child
        assert child_process.is_running()
        assert j.sal.nettools.waitConnectionTest("localhost", 2015)
