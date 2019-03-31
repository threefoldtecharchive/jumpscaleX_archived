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
        j.builder.runtimes.golang.get('github.com/coredns/coredns', install=False, update=True)

        # go to package path and build (for coredns)
        C="""
        cd {DIR_BUILD}
        git remote add threefoldtech_coredns https://github.com/threefoldtech/coredns
        git fetch threefoldtech_coredns
        git checkout threefoldtech_coredns/master
        make
        """
        j.builder.tools.execute(C)


    @builder_method()
    def install(self):
        """
        kosmos 'j.builder.network.coredns.install()'

        installs and runs coredns server with redis plugin
        """

        self.execute("cp {GITDIR}/coredns/coredns /sandbox/bin/coredns")

        #WRITE THE CONFIG FILE IN THE SANDBOX DIR /sandbox/cfg/coredns.conf


    @property
    def startup_cmds(self):
        cmd = "/sandbox/bin/coredns -conf /sandbox/cfg/coredns.conf"
        cmds = [j.data.startupcmd.get(cmd)]
        return cmds

    @builder_method()
    def sandbox(self):
        coredns_bin = j.sal.fs.joinPaths(self._package_path, 'coredns')
        dir_dest = j.sal.fs.joinPaths(self.DIR_PACKAGE, coredns_bin[1:])
        j.builder.tools.dir_ensure(dir_dest)
        j.sal.fs.copyFile(coredns_bin, dir_dest)

        dir_dest = j.sal.fs.joinPaths(self.DIR_PACKAGE, self.DIR_PACKAGE, 'etc/ssl/certs/')
        j.builder.tools.dir_ensure(dir_dest)
        j.sal.fs.copyDirTree('/etc/ssl/certs', dir_dest)

        #copy the /sandbox/cfg/coredns.conf to the sandbox dir
        #TODO:*1





    @builder_method()
    def test(self):
        if self.running():
            self.stop()

        self.start()

        client = j.clients.coredns.get("test_builder", "etcd_instance")
        client.zone_create("example.com", "0.0.0.0")
        client.deploy()

    @builder_method()
    def test_zos(self, zos_client, flist=None, build=False):
        if build:
            flist = self.sandbox(flist_create=True)

        if not flist:
            flist = "TODO: the official flist for coredns"

        container = zos_client.container.create("test_coredns_builder", flist)
        # TODO: do more tests on the created container

