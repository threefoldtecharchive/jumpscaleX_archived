from Jumpscale import j
from Jumpscale.builder.runtimes.BuilderGolang import BuilderGolangTools

builder_method = j.builder.system.builder_method

CONFIG_TEMPLATE = """
namespace: default  # 0-db namespace (required)
datastor: # required
  # the address(es) of a 0-db cluster (required0)
  shards: # required
    - 127.0.0.1:9900
  pipeline:
    block_size: 4096
    compression: # optional
      type: snappy # snappy is the default
      mode: default # default is the default
metastor: # required
  db: # required
    # the address(es) of an etcd server cluster
    type: "etcd"
    config:
        endpoints:
        - 127.0.0.1:2379
  encoding: protobuf
"""


class BuilderZeroStor(BuilderGolangTools):
    NAME = "zstor"

    def _init(self):
        super()._init()
        self.datadir = ""

    def profile_builder_set(self):
        super().profile_builder_set()

    @builder_method()
    def build(self):
        """
        Builds zstor
        """
        j.builder.runtimes.golang.install()
        self.get("github.com/threefoldtech/0-stor/cmd/zstor")

        # Make
        cmd = "cd {}/src/github.com/threefoldtech/0-stor && make".format(self.DIR_GO_PATH)
        j.sal.process.execute(cmd)

    @builder_method()
    def install(self):
        """
        Installs zstor
        """
        self._copy("{}/src/github.com/threefoldtech/0-stor/bin".format(self.DIR_GO_PATH), "{DIR_BIN}")

        j.sal.fs.writeFile(filename="/sandbox/cfg/zstor.yaml", contents=CONFIG_TEMPLATE)

    @property
    def startup_cmds(self):
        """
        Starts zstor
        """
        self.datadir = self.DIR_BUILD
        self.tools.dir_ensure(self.datadir)

        cmd = "zstor --config /sandbox/cfg/zstor.yaml daemon --listen 127.0.0.1:8000"
        cmds = [j.tools.startupcmd.get(name=self.NAME, cmd=cmd)]
        return cmds

    @builder_method()
    def clean(self):
        """
        Remove built files
        """
        self._remove(self.DIR_SANDBOX)
        self._remove("{}/src/github.com/threefoldtech/0-stor/".format(self.DIR_GO_PATH))

    @builder_method()
    def sandbox(self):
        """
        Copy required bin files to be used to sandbox
        """
        bin_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox", "bin")
        self.tools.dir_ensure(bin_dest)
        bin_path = j.sal.fs.joinPaths(self._replace("{DIR_BIN}"), self.NAME)
        bin_bench_path = j.sal.fs.joinPaths(self._replace("{DIR_BIN}"), "zstorbench")
        self._copy(bin_path, bin_dest)
        self._copy(bin_bench_path, bin_dest)

    @builder_method()
    def test(self):
        if self.running():
            self.stop()

        self.start()
        pid = j.sal.process.getProcessPid(self.NAME)
        assert pid is not []
        self.stop()

        print("TEST OK")

    @builder_method()
    def uninstall(self):
        """
        Uninstall zstor by removing all related files from bin directory and build destination
        """
        bin_path = self.tools.joinpaths("{DIR_BIN}", self.NAME)
        bin_bench_path = self.tools.joinpaths("{DIR_BIN}", "zstorbench")
        self._remove(bin_path)
        self._remove(bin_bench_path)
        self.clean()
