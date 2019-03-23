from Jumpscale import j

class BuilderEthereum(j.builder.system._BaseClass):
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

        j.builder.runtimes.golang.execute("cd {} && go build -a -ldflags '-w -extldflags -static' ./cmd/geth".format(self.package_path))
        j.builder.runtimes.golang.execute("cd {} && go build -a -ldflags '-w -extldflags -static' ./cmd/bootnode".format(self.package_path))

        self._done_set('build')

    def install(self, reset=False):
        """
        Install the binaries of ethereum
        """
        if self._done_get('install') and reset is False:
            return

        self.build(reset=reset)

        bin_path = self.tools.joinpaths(self.package_path, "geth")
        self.tools.file_copy(bin_path, "/sandbox/bin")
        self._done_set('install')

    def stop(self, pid=None, sig=None):
        """Stops geth process

        :param pid: pid of the process, if not given, will kill by name
        :type pid: long, defaults to None
        :param sig: signal, if not given, SIGKILL will be used
        :type sig: int, defaults to None
        """
        if pid:
            j.sal.process.kill(pid, sig)
        else:
            j.sal.process.killProcessByName(self.NAME, sig)

    def sandbox(self, sandbox_dir="/tmp/builder/ethereum", flist=True, hub_instance=None, reset=False):
        """
        sandbbox go-ethereum
        :param sandbox_dir: the directory to sandbox to (default: {"/tmp/builder/ethereum"})
        :param create_flist: if True and flist will be created after sandboxing (default: {False})
        :param hub_instance: zhub_client instance which will be used to uplload the flist (default: {None})
        :param reset: reset the process (default: {False})
        """
        if self._done_check('sandbox') and not reset:
            return
        self.build(reset = reset)

        bin_path = self.tools.joinpaths(self.package_path, "geth")
        bin_dest = self.tools.joinpaths(sandbox_dir, 'sandbox', 'bin')
        self.tools.dir_ensure(bin_dest)
        self.tools.file_copy(bin_path, bin_dest)
        
        bootnode_bin_path = self.tools.joinpaths(self.package_path, "bootnode")
        bootnode_bin_dest = self.tools.joinpaths(sandbox_dir, 'sandbox', 'bin')
        self.tools.dir_ensure(bootnode_bin_dest)
        self.tools.file_copy(bootnode_bin_path, bootnode_bin_dest)

        if flist:
            print(self.flist_create(sandbox_dir=sandbox_dir, hub_instance=hub_instance))
        self._done_set('sandbox')

