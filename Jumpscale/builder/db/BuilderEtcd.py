from Jumpscale import j


class BuilderEtcd(j.builder.system._BaseClass):
    NAME = 'etcd'

    def build(self, reset=False):
        """
        Build etcd
        """
        def do():
            if self._done_check('build', reset):
                    return
            j.sal.fs.remove('/tmp/etcd')
            # j.builder.runtimes.golang.install()

            _script = """
            cd /tmp
            # git clone https://github.com/coreos/etcd.git
            cd etcd
            ./build
            """
            j.sal.process.execute(_script, timeout=10000000000000000000)

            self._done_set('build')
        do()
        # self._cache.get(key='build', method=do, expire=3600*30*24, refresh=False, retry=2, die=True)

    def sandbox(self):
        def do():
            if self._done_check('sandbox'):
                return
            if not self._done_check('build'):
                self.build()

            path = '/tmp/etcd/bin'
            j.sal.fs.copyFile(j.sal.fs.joinPaths(path, 'etcd'), j.core.dirs.BINDIR)
            j.sal.fs.copyFile(j.sal.fs.joinPaths(path, 'etcdctl'), j.core.dirs.BINDIR)

            self._done_set('sandbox')

        self._cache.get(key="sandbox", method=do, expire=3600*30*24, refresh=False, retry=1, die=True)

    def client_get(self, name):
        """
        return the client to the installed server, use the config params of the server to create a client for
        :return:
        """
        return j.clients.etcd.get(name)

    def test(self):
        """
        js_shell 'j.builder._template.test()'
        :return:
        """
        #TODO: check that test instance is running, if so stop
        #TODO: build/sandbox a server (or component)
        #TODO: call the component call start/stop/... to test
        #TODO: create a client to the server (use j.clients....) and connect to server if a server
        #TODO: do some test on the server (use the component.test... method)
        pass

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

        self._logger.info('building flist')
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
            self._logger.info("uploading flist to the hub")
            hub.upload(tarfile)
            self._logger.info("uploaded at https://hub.gig.tech/%s/etcd-3.3.4.flist", hub.config.data['username'])

        return tarfile
