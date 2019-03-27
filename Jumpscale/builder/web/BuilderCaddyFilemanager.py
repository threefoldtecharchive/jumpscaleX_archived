from Jumpscale import j


class BuilderCaddyFilemanager(j.builder.system._BaseClass):
    NAME = 'filemanager'
    PLUGINS = ['iyo', 'filemanager']

    def _init(self):
        self.go_runtime = j.builder.runtimes.golang
        self.templates_dir = self.tools.joinpaths(
            j.sal.fs.getDirName(__file__), 'templates')
        # self.root_dirs = {
        #     '/etc/ssl/certs': '/etc/ssl/certs'
        # }

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

   
    def sandbox(self, dest_path='/tmp/builder/caddyfilemanager',create_flist=True, zhub_instance=None, reset=False):

        '''Copy built bins to dest_path and create flist if create_flist = True

        :param dest_path: destination path to copy files into
        :type dest_path: str
        :param sandbox_dir: path to sandbox
        :type sandbox_dir: str
        :param reset: reset sandbox file transfer
        :type reset: bool
        :param create_flist: create flist after copying files
        :type create_flist:bool
        :param zhub_instance: hub instance to upload flist to
        :type zhub_instance:str
        '''

        if self._done_check('sandbox') and reset is False:
             return
        self.build(reset = reset)

        caddy_bin_path = self.tools.joinpaths(self.go_runtime.go_path_bin, 'caddy')
        bin_dest = self.tools.joinpaths(dest_path, 'sandbox', 'bin')
        self.tools.dir_ensure(bin_dest)

        self.root_dirs = {
            '/etc/ssl/certs': '/etc/ssl/certs'
        }

        # empty dirs
        self.tools.dir_ensure(self.tools.joinpaths(dest_path, 'sandbox', 'var', 'log'))
        self.tools.dir_ensure(self.tools.joinpaths(dest_path, 'sandbox', 'filemanager', 'files'))

        cfg_dir = self.tools.joinpaths(dest_path, 'sandbox', 'cfg', 'filemanager')
        
        # bin
        self.tools.file_copy(caddy_bin_path, bin_dest)

        # caddy config
        caddyfile = self.tools.joinpaths(self.templates_dir, 'filemanager_caddyfile')
        self.tools.file_copy(self.tools.joinpaths(cfg_dir, caddyfile))

        # startup
        startup_file = self.tools.joinpaths(self.templates_dir, 'filemanager_startup.toml')
        self.startup = j.sal.fs.readFile(startup_file)
        file_dest = self.tools.joinpaths(dest_path, '.startup.toml')
        j.builder.tools.file_ensure(file_dest)
        j.builder.tools.file_write(file_dest, self.startup)

        # copy /etc/ssl/cert
        certs = self.tools.joinpaths(dest_path, 'etc', 'ssl', 'certs')
        self.tools.dir_ensure(certs)
        j.builder.tools.copyTree(source='/etc/ssl/certs', dest=certs)
        if create_flist:
            print(self.flist_create(sandbox_dir=dest_path, hub_instance=zhub_instance))
        self._done_set('sandbox') 