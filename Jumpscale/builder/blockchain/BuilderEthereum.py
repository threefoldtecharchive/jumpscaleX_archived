from Jumpscale import j

class BuilderEthereum(j.builder.system._BaseClass):
    """
    NOTE: This not a completed builder, this builder is made to demonstrate how to create a builder
    """
    # TODO: build the other binaries and write a startup script

    NAME = "geth"

    def _init(self):
        self.geth_repo = "github.com/ethereum/go-ethereum"
        self.package_path = j.builder.runtimes.golang.package_path_get("ethereum/go-ethereum")


    def build(self, reset=False):
        """Build the binaries of ethereum
        Keyword Arguments:
            reset {bool} -- reset the build process (default: {False})
        """

        if self._done_get('build') and reset is False:
            return

        if not j.builder.runtimes.golang.is_installed:
            j.builder.runtimes.golang.install()

        j.builder.runtimes.golang.get(self.geth_repo)

        j.builder.runtimes.golang.execute("cd {} && make geth".format(self.package_path))
        self._done_set('build')

    def install(self, reset=False):
        """
        Install the binaries of ethereum
        """
        if self._done_get('install') and reset is False:
            return

        self.build(reset=reset)

        bin_path = self.tools.joinpaths(self.package_path, "build", "bin", "geth")
        self.tools.file_copy(bin_path, "/sandbox/bin")
        self._done_set('install')

    def sandbox(self, sandbox_dir="/tmp/builder/ethereum", flist=False, hub_instance=None, reset=False):
        """
        sandbbox go-ethereum
        :param sandbox_dir: the directory to sandbox to (default: {"/tmp/builder/ethereum"})
        :param create_flist: if True and flist will be created after sandboxing (default: {False})
        :param hub_instance: zhub_client instance which will be used to uplload the flist (default: {None})
        :param reset: reset the process (default: {False})
        """
        if self._done_get('sandbox') and reset is False:
            return

        self.build(reset=reset)
        bin_path = self.tools.joinpaths(self.package_path, "build", "bin", "geth")
        bin_dest = self.tools.joinpaths(sandbox_dir, 'sandbox', 'bin')
        self.tools.dir_ensure(bin_dest)
        self.tools.file_copy(bin_path, bin_dest)

        if flist:
            print(self.flist_create(sandbox_dir=sandbox_dir, hub_instance=hub_instance))

        self._done_set('sandbox')
