from Jumpscale import j


class BuilderEtcd(j.builder.system._BaseClass):
    NAME = 'etcd'

    def _init(self):
        self.package_path = j.builder.runtimes.golang.package_path_get('etcd', host='go.etcd.io')
        startup_file = j.sal.fs.joinPaths(j.sal.fs.getDirName(__file__), 'templates', 'etcd_startup.toml')
        self.startup = j.sal.fs.readFile(startup_file)




    def build(self, reset=False):
        """
        Build etcd
        """
        if self._done_check('build', reset):
            return

        j.builder.runtimes.golang.install()
        # get a vendored etcd from master
        j.builder.runtimes.golang.get('go.etcd.io/etcd', install=False, update=False)
        # go to package path and build (for etcdctl)
        j.builder.runtimes.golang.execute('cd %s && ./build' % self.package_path)

        self._done_set('build')
        # self._cache.get(key='build', method=do, expire=3600*30*24, refresh=False, retry=2, die=True)

    def sandbox(self):
        def do():
            if self._done_check('sandbox'):
                return
            if not self._done_check('build'):
                self.build()

            j.sal.fs.copyFile(j.sal.fs.joinPaths(self.package_path, 'bin', 'etcd'), j.core.dirs.BINDIR)
            j.sal.fs.copyFile(j.sal.fs.joinPaths(self.package_path, 'bin', 'etcdctl'), j.core.dirs.BINDIR)

            self._done_set('sandbox')

        #self._cache.get(key="sandbox", method=do, expire=3600*30*24, refresh=False, retry=1, die=True)

    def client_get(self, name):
        """
        return the client to the installed server, use the config params of the server to create a client for
        :return:
        """
        return j.clients.etcd.get(name)

    def _test(self, name=''):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key='test_main')

    def build_flist(self, hub_instance=None):
        """
        build a flist for etcd

        This method builds and optionally upload the flist to the hub

        :param hub_instance: instance name of the zerohub client to use to upload the flist, defaults to None
        :param hub_instance: str, optional
        :raises j.exceptions.Input: raised if the zerohub client instance does not exist in the config manager
        :return: path to the tar.gz created
        :rtype: str
        """
        self.sandbox()

        self._log_info('building flist')
        build_dir = j.sal.fs.getTmpDirPath()
        tarfile = '/tmp/etcd-3.3.4.tar.gz'
        bin_dir = j.sal.fs.joinPaths(build_dir, 'bin')
        j.core.tools.dir_ensure(bin_dir)
        j.builder.tools.file_copy(j.sal.fs.joinPaths(j.core.dirs.BINDIR, 'etcd'), bin_dir)
        j.builder.tools.file_copy(j.sal.fs.joinPaths(j.core.dirs.BINDIR, 'etcdctl'), bin_dir)

        j.sal.process.execute('tar czf {} -C {} .'.format(tarfile, build_dir))

        if hub_instance:
            if not j.clients.zerohub.exists(hub_instance):
                raise j.exceptions.Input("hub instance %s does not exists, can't upload to the hub" % hub_instance)
            hub = j.clients.zerohub.get(hub_instance)
            hub.authentificate()
            self._log_info("uploading flist to the hub")
            hub.upload(tarfile)
            self._log_info("uploaded at https://hub.gig.tech/%s/etcd-3.3.4.flist", hub.config.data['username'])

        return tarfile
