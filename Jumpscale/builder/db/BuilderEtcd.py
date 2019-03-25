from Jumpscale import j


ETCD_CONFIG="""
name: "etcd_builder"
data-dir: "/mnt/data"
listen-peer-urls: "http://0.0.0.0:2380"
listen-client-urls: "http://0.0.0.0:2379"
initial-advertise-peer-urls: "http://'$node_addr':2380"
"""

class BuilderEtcd(j.builder.system._BaseClass):
    NAME = 'etcd'

    def _init(self):
        self.package_path = j.builder.runtimes.golang.package_path_get('etcd', host='go.etcd.io')

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

    def install(self,reset=False):
        if self._done_check('install', reset):
            return

        self.build(reset=reset)

        bin_dest = j.sal.fs.joinPaths(dest_path, j.core.dirs.BINDIR[1:])
        j.builder.tools.dir_ensure(bin_dest)
        j.sal.fs.copyFile(j.sal.fs.joinPaths(self.package_path, 'bin', 'etcd'), bin_dest)
        j.sal.fs.copyFile(j.sal.fs.joinPaths(self.package_path, 'bin', 'etcdctl'), bin_dest)

        self._done_set('install')


    def start(self):

        C="""
        etcdctl  user add root:{etcd_password}
        etcdctl  auth enable
        etcdctl  --user=root:$etcd_password put "traefik/acme/account" "foo"
        etcd --config-file etcd.conf
        """
        j.shell()


    def sandbox(self, dest_path="/tmp/builders/etcd", reset=False, create_flist=False, zhub_instance=None):
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
        if self._done_check('sandbox', reset):
            return

        self.install(reset=reset)

        dir_dest = j.sal.fs.joinPaths(dest_path, 'sandbox')
        j.builder.tools.dir_ensure(dir_dest)
        startup_file = j.sal.fs.joinPaths(j.sal.fs.getDirName(__file__), 'templates', 'etcd_startup.toml')
        self.startup = j.sal.fs.readFile(startup_file)
        j.sal.fs.copyFile(startup_file,   dir_dest)

        self._done_set('sandbox')

        if create_flist:
            self.flist_create(dest_path, zhub_instance)

    def client_get(self, name):
        """
        return the client to the installed server, use the config params of the server to create a client for
        :return:
        """
        return j.clients.etcd.get(name)

    def test(self):

        self.stop()
        self.build(reset=True)
        self.sandbox()
    
        # try to start/stop
        tmux_pane = j.servers.etcd.start()
        tmux_process = tmux_pane.process_obj
        child_process = tmux_pane.process_obj_child
        assert child_process.is_running()
    
        client = self.client_get('etcd_test')
        j.sal.nettools.waitConnectionTest(client.host, client.port)
        client.api.put('foo', 'etcd_bar')
        assert client.get('foo') == 'etcd_bar'
        j.servers.etcd.stop(tmux_process.pid)

        print ("TEST OK")



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
