from Jumpscale import j
from Jumpscale.builder.runtimes.BuilderGolang import BuilderGolangTools

builder_method = j.builder.system.builder_method


class BuilderEthereum(BuilderGolangTools):
    NAME = "geth"

    def _init(self):
        super()._init()
        self.geth_repo = "github.com/ethereum/go-ethereum"
        self.package_path = self.package_path_get("ethereum/go-ethereum")

    @builder_method()
    def build(self, reset=False):
        """Build the binaries of ethereum
        Keyword Arguments:
            reset {bool} -- reset the build process (default: {False})
        """
        j.builder.runtimes.golang.install()

        self.get(self.geth_repo)

        self._execute("cd {} && go build -a -ldflags '-w -extldflags -static' ./cmd/geth".format(self.package_path))
        self._execute("cd {} && go build -a -ldflags '-w -extldflags -static' ./cmd/bootnode".format(self.package_path))

    @builder_method()
    def install(self, reset=False):
        """
        Install the binaries of ethereum
        """
        bin_path = self.tools.joinpaths(self.package_path, self.NAME)
        self.tools.dir_ensure('{DIR_BIN}')
        self.tools.file_copy(bin_path, self._replace('{DIR_BIN}'))

    @property
    def startup_cmds(self):
        cmd = j.tools.startupcmd.get("geth", cmd='geth')
        return [cmd]

    @builder_method()
    def sandbox(self, zhub_client=None, flist_create=True):
        """
        sandbox go-ethereum
        Copy built bins and config files to sandbox specific directory and create flist and upload it to the hub if flist_create is True
            :param zhub_client: hub instance to upload flist to
            :type zhub_client:str
            :param flist_create: create flist after copying files
            :type flist_create:bool
        """
        dir_dest = j.sal.fs.joinPaths(
            "/sandbox/var/build", "{}/sandbox".format(self.DIR_SANDBOX)
        )
        bin_path = self.tools.joinpaths(self._replace("{DIR_BIN}"), self.NAME)
        bin_dest = self.tools.joinpaths(dir_dest, "bin", self.NAME)
        self.tools.dir_ensure(bin_dest)
        self.tools.file_copy(bin_path, bin_dest)

        bootnode_bin_path = self.tools.joinpaths(self.package_path, "bootnode")
        bootnode_bin_dest = self.tools.joinpaths(dir_dest, "bin", self.NAME)
        self.tools.dir_ensure(bootnode_bin_dest)
        self.tools.file_copy(bootnode_bin_path, bootnode_bin_dest)

    def test(self):
        '''Tests the builder by performing the following:
        build(), install(), start()-> geth running, stop()-> geth not running
        '''
        if self.running():
            self.stop()
        self.build(reset=True)
        self.install()

        assert not self.running()
        # check start is working
        self.start()
        assert self.running()
        # check stop is working
        self.stop()
        assert not self.running()
        self._log_info("Ethereum test successfull")
