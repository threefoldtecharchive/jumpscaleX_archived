from Jumpscale import j

builder_method = j.builder.system.builder_method

class BuilderCoreDns(j.builder.system._BaseClass):
    NAME = "coredns"

    @builder_method(log=True, done_check=True)
    def _init(self, reset=False):
        self.golang = j.builder.runtimes.golang
        self._package_path = j.builder.runtimes.golang.package_path_get('coredns', host='github.com/coredns')

    @builder_method(log=True, done_check=True)
    def build(self, reset=False):
        """
        kosmos 'j.builder.network.coredns.build(reset=False)'

        installs and runs coredns server with redis plugin
        """

        # install golang
        j.builder.runtimes.golang.install(reset=reset)
        j.builder.runtimes.golang.get('github.com/coredns/coredns', install=False, update=True)

        # go to package path and build (for coredns)
        C="""
        cd {GITDIR}
        git remote add threefoldtech_coredns https://github.com/threefoldtech/coredns
        git fetch threefoldtech_coredns
        git checkout threefoldtech_coredns/master
        make

        cp /sandbox/go_proj/src/github.com/coredns/coredns/coredns /sandbox/bin/coredns
        """
        j.builder.tools.run(C, args={"GITDIR":self._package_path}, replace=True)

    @property
    def startup_cmds(self):
        cmd = """
        echo '''. {
    etcd $domain {
        stubzones
        path /hosts
        endpoint $etcd_endpoint
        fallthrough
        debug
    }
    loadbalance
    reload 5s
}''' > coredns.conf

        """
        cmd += "{coredns_path}/coredns -conf coredns.conf".format(coredns_path=self._package_path)
        cmds = [j.data.startupcmd.get(cmd)]
        return cmds

    @builder_method(log=True, done_check=True)
    def sandbox(self, reset=False, flist_create=True):
        coredns_bin = j.sal.fs.joinPaths(self._package_path, 'coredns')
        dir_dest = j.sal.fs.joinPaths(self._sandbox_dir, coredns_bin[1:])
        j.builder.tools.dir_ensure(dir_dest)
        j.sal.fs.copyFile(coredns_bin, dir_dest)

        dir_dest = j.sal.fs.joinPaths(self._sandbox_dir, self._sandbox_dir, 'etc/ssl/certs/')
        j.builder.tools.dir_ensure(dir_dest)
        j.sal.fs.copyDirTree('/etc/ssl/certs', dir_dest)

        startup_file = j.sal.fs.joinPaths(j.sal.fs.getDirName(__file__), 'templates', 'coredns_startup.toml')
        self.startup = j.sal.fs.readFile(startup_file)
        j.sal.fs.copyFile(startup_file,  j.sal.fs.joinPaths(self._sandbox_dir, self._sandbox_dir))

        if flist_create:
            return self._flist_create()

    @builder_method(log=True, done_check=True)
    def test(self):
        if self.running():
            self.stop()

        self.start()

        client = j.clients.coredns.get("test_builder", "etcd_instance")
        client.zone_create("example.com", "0.0.0.0")
        client.deploy()

    @builder_method(log=True, done_check=True)
    def test_zos(self, zos_client, flist=None, build=False):
        if build:
            flist = self.sandbox(flist_create=True)

        if not flist:
            flist = "TODO: the official flist for coredns"

        container = zos_client.container.create("test_coredns_builder", flist)
        # TODO: do more tests on the created container

