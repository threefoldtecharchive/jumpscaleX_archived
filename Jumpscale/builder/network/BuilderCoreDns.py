from Jumpscale import j
from Jumpscale.builder.runtimes.BuilderGolang import BuilderGolangTools

builder_method = j.builder.system.builder_method


CONFIGTEMPLATE = """
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


class BuilderCoreDns(BuilderGolangTools, j.builder.system._BaseClass):
    NAME = "coredns"

    def _init(self):
        super()._init()
        self.package_path = self.package_path_get(self.NAME)

    @builder_method()
    def build(self):
        """
        kosmos 'j.builder.network.coredns.build(reset=True)'

        installs and runs coredns server with redis plugin
        """

        # install golang
        j.builder.runtimes.golang.install()
        j.builder.db.etcd.install()
        self.tools.dir_ensure(self.package_path)

        # https://github.com/coredns/coredns#compilation-from-source

        # go to package path and build (for coredns)
        C = """
        cd {}
        git clone https://github.com/coredns/coredns.git
        cd coredns
        make
        """.format(self.package_path)
        self._execute(C, timeout=1000)

    @builder_method()
    def install(self):
        """
        kosmos 'j.builder.network.coredns.install()'

        installs and runs coredns server with redis plugin
        """
        src = self.tools.joinpaths(self.package_path, self.NAME, self.NAME)
        self._copy(src, '{DIR_BIN}/coredns')
        j.sal.fs.writeFile(filename='/sandbox/cfg/coredns.conf', contents=CONFIGTEMPLATE)

    def clean(self):
        self._remove(self.package_path)
        self._remove(self.DIR_SANDBOX)

    @property
    def startup_cmds(self):
        cmd = "/sandbox/bin/coredns -conf /sandbox/cfg/coredns.conf"
        cmds = [j.tools.startupcmd.get(name='coredns', cmd=cmd)]
        return cmds

    @builder_method()
    def sandbox(self, zhub_client=None, flist_create=False):
        coredns_bin = j.sal.fs.joinPaths('{DIR_BIN}', self.NAME)
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

    @builder_method()
    def reset(self):
        super().reset()
        self.clean()

    @builder_method()
    def test_zos(self, zos_client="", zhub_client=""):
        self.sandbox(zhub_client=zhub_client, flist_create=True)
        flist = '/tmp/{}.tar.gz'.format(self.NAME)
        test_container = zos_client.containers.create(name="test_coredns", flist=flist)
        test_container.start()
        client = test_container.client
        assert client.ping()
        print("TEST OK")