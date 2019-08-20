from Jumpscale import j

builder_method = j.builders.system.builder_method


class BuilderZeroFlist(j.builders.system._BaseClass):
    NAME = "zflist"

    def _init(self, **kwargs):
        super()._init()
        self.datadir = ""

    def profile_builder_set(self):
        super().profile_builder_set()

    @builder_method()
    def build(self):
        """
        Builds zflist
        """
        cmd = """
        rm /opt/*
        cd /sandbox/code/github/threefoldtech
        rm -rf 0-flist/
        git clone -b development-v2 https://github.com/threefoldtech/0-flist.git

        cd 0-flist/autobuild/
        bash zflist.sh

        cd ..
        make

        """
        j.sal.process.execute(cmd)

    @builder_method()
    def install(self):
        """
        Installs zflist
        """
        self.build()
        self._copy("/sandbox/code/github/threefoldtech/0-flist/zflist/zflist", "{DIR_BIN}")

    @property
    def startup_cmds(self):
        """
        Starts zflist
        """
        self.datadir = self.DIR_BUILD
        self.tools.dir_ensure(self.datadir)

        cmd = "zstor --config /sandbox/cfg/zstor.yaml daemon --listen 127.0.0.1:8000"
        cmd_zdb = j.builder.db.zdb.startup_cmds
        cmd_etcd = j.builder.db.etcd.startup_cmds
        cmds = [j.servers.startupcmd.get(name=self.NAME, cmd_start=cmd)]
        return cmd_zdb + cmd_etcd + cmds

    @builder_method()
    def clean(self):
        """
        Remove built files
        """
        self._remove(self.DIR_SANDBOX)
        self._remove("/sandbox/code/github/threefoldtech/0-flist")
        self._remove("/opt/")

    @builder_method()
    def sandbox(self):
        """
        Copy required bin files to be used to sandbox
        """
        # Copy zstor bins
        bin_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox", "bin")
        self.tools.dir_ensure(bin_dest)
        bin_path = j.sal.fs.joinPaths(self._replace("{DIR_BIN}"), self.NAME)
        self._copy(bin_path, bin_dest)

    @builder_method()
    def uninstall(self):
        """
        Uninstall zflist by removing all related files from bin directory and build destination
        """
        bin_path = self.tools.joinpaths("{DIR_BIN}", self.NAME)
        self._remove(bin_path)
        self.clean()
