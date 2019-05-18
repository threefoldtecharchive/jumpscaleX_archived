from Jumpscale import j
from Jumpscale.builder.runtimes.BuilderGolang import BuilderGolangTools

builder_method = j.builder.system.builder_method


class BuilderEtcd(BuilderGolangTools):
    NAME = "etcd"

    def _init(self):
        super()._init()

    def profile_builder_set(self):
        super().profile_builder_set()
        self.profile.env_set("GO111MODULE", "on")

    @builder_method()
    def build(self):
        """
        Build etcd
        """
        j.builder.runtimes.golang.install()
        # https://github.com/etcd-io/etcd/blob/master/Documentation/dl_build.md#build-the-latest-version
        self.get("go.etcd.io/etcd")
        self.get("go.etcd.io/etcd/etcdctl")

    @builder_method()
    def install(self):
        j.builder.tools.file_copy("%s/etcd" % self.DIR_GO_PATH_BIN, "{DIR_BIN}/etcd")
        j.builder.tools.file_copy("%s/etcdctl" % self.DIR_GO_PATH_BIN, "{DIR_BIN}/etcdctl")

    @property
    def startup_cmds(self):
        return [j.tools.startupcmd.get(name=self.NAME, cmd=self.NAME)]

    @builder_method()
    def sandbox(
        self,
        reset=False,
        zhub_client=None,
        flist_create=False,
        merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-development.flist",
    ):
        '''
        Copy built bins to dest_path and create flist if create_flist = True
        :param dest_path: destination path to copy files into
        :type dest_path: str
        :param sandbox_dir: path to sandbox
        :type sandbox_dir: str
        :param reset: reset sandbox file transfer
        :param create_flist: create flist after copying files
        :type create_flist:bool
        :param zhub_instance: hub instance to upload flist to
        :type zhub_instance:str
        """
        self.install()
        bin_dest = j.sal.fs.joinPaths("/sandbox/var/build", "{}/sandbox".format(self.DIR_SANDBOX))
        self.tools.dir_ensure(bin_dest)
        etcd_bin_path = self.tools.joinpaths("{DIR_BIN}", self.NAME)
        etcdctl_bin_path = self.tools.joinpaths("{DIR_BIN}", "etcdctl")
        self.tools.file_copy(etcd_bin_path, bin_dest)
        self.tools.file_copy(etcdctl_bin_path, bin_dest)

        if create_flist:
            self.flist_create(bin_dest, zhub_instance)

        lib_dest = self.tools.joinpaths(dest_path, 'sandbox/lib')
        self.tools.dir_ensure(lib_dest)
        for bin in bins:
            dir_src = self.tools.joinpaths(j.core.dirs.BINDIR, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest, exclude_sys_libs=False)
        '''

    def client_get(self, name):
        """
        return the client to the installed server, use the config params of the server to create a client for
        :return:
        """
        return j.clients.etcd.get(name)

    def test(self):

        self.stop()
        self.install()
        self.sandbox()

        # try to start/stop
        tmux_pane = j.servers.etcd.start()
        tmux_process = tmux_pane.process_obj
        child_process = tmux_pane.process_obj_child
        assert child_process.is_running()

        client = self.client_get("etcd_test")
        j.sal.nettools.waitConnectionTest(client.host, client.port)
        client.api.put("foo", "etcd_bar")
        assert client.get("foo") == "etcd_bar"
        j.servers.etcd.stop(tmux_process.pid)

        print("TEST OK")

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

        self._log_info("building flist")
        build_dir = j.sal.fs.getTmpDirPath()
        tarfile = "/tmp/etcd-3.3.4.tar.gz"
        bin_dir = j.sal.fs.joinPaths(build_dir, "bin")
        j.core.tools.dir_ensure(bin_dir)
        j.builder.tools.file_copy(j.sal.fs.joinPaths(j.core.dirs.BINDIR, "etcd"), bin_dir)
        j.builder.tools.file_copy(j.sal.fs.joinPaths(j.core.dirs.BINDIR, "etcdctl"), bin_dir)

        j.sal.process.execute("tar czf {} -C {} .".format(tarfile, build_dir))

        if hub_instance:
            if not j.clients.zerohub.exists(hub_instance):
                raise j.exceptions.Input("hub instance %s does not exists, can't upload to the hub" % hub_instance)
            hub = j.clients.zerohub.get(hub_instance)
            hub.authentificate()
            self._log_info("uploading flist to the hub")
            hub.upload(tarfile)
            self._log_info("uploaded at https://hub.grid.tech/%s/etcd-3.3.4.flist", hub.config.data["username"])

        return tarfile
