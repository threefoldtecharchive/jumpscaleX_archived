from Jumpscale import j

builder_method = j.builder.system.builder_method


CONFIGTEMPLATE="""
.{
    etcd $domain {
        stubzones
        path /hosts
        endpoint $etcd_endpoint
        fallthrough
        debug
    }
    loadbalance
    reload 5s
}        
"""

class BuilderCoreDns(j.builder.system._BaseClass):
    NAME = "coredns"

    def _init(self, reset=False):
        self.DIR_BUILD = j.builder.runtimes.golang.package_path_get('coredns', host='github.com/coredns')

    @builder_method()
    def build(self):
        """
        kosmos 'j.builder.network.coredns.build(reset=True)'

        installs and runs coredns server with redis plugin
        """

        # install golang
        j.builder.runtimes.golang.install()
        j.builder.db.etcd.install()
        j.builder.runtimes.golang.get('github.com/coredns/coredns', install=False, update=True)
        
        # go to package path and build (for coredns)
        C="""
        cd {DIR_BUILD}
        git remote add threefoldtech_coredns https://github.com/threefoldtech/coredns
        git fetch threefoldtech_coredns
        git checkout threefoldtech_coredns/master
        make
        """
        self._execute(C)

    @builder_method()
    def install(self):
        """
        kosmos 'j.builder.network.coredns.install()'

        installs and runs coredns server with redis plugin
        """
        self._copy(src='{DIR_BUILD}/coredns', dst='/sandbox/bin/coredns')
        j.sal.fs.writeFile(filename='/sandbox/cfg/coredns.conf', contents=CONFIGTEMPLATE)

    def clean(self):
        self._remove(self.DIR_BUILD)
        self._remove(self.DIR_SANDBOX)
    
    @property
    def startup_cmds(self):
        cmd = "/sandbox/bin/coredns -conf /sandbox/cfg/coredns.conf"
        cmds = [j.tools.startupcmd.get(name='coredns', cmd=cmd)]
        return cmds

    @builder_method()
    def sandbox(self):
        coredns_bin = j.sal.fs.joinPaths(self.DIR_BUILD, self.NAME)
        dir_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, 'sandbox')
        self.tools.dir_ensure(dir_dest)
        self._copy(coredns_bin, dir_dest)

        dir_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, 'etc/ssl/certs/')
        self.tools.dir_ensure(dir_dest)
        self._copy('/etc/ssl/certs', dir_dest)
        self._copy('/sandbox/cfg/coredns.conf', self.DIR_SANDBOX)

    @builder_method()
    def test(self):
        if self.running():
            self.stop()

        j.servers.etcd.start()
        self.start()
        j.clients.etcd.get('test_coredns')
        client = j.clients.coredns.get(name='test_builder', etcd_instance='test_coredns')
        client.zone_create("example.com", "0.0.0.0")
        client.deploy()
        self.stop()
        j.servers.etcd.stop()

        print('TEST OK')

    @builder_method()
    def uninstall(self):
        bin_path = self.tools.joinpaths("{DIR_BIN}", self.NAME)
        self._remove(bin_path)
        self.clean()
        self.clean()

    @builder_method()
    def test_zos(self, zos_client, flist=None, build=False):
        if build:
            flist = self.sandbox(flist_create=True)

        if not flist:
            flist = "TODO: the official flist for coredns"

        container = zos_client.container.create("test_coredns_builder", flist)
        # TODO: do more tests on the created container
