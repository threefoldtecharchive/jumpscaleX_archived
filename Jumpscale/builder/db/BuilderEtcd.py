from Jumpscale import j
from Jumpscale.builder.runtimes.BuilderGolang import BuilderGolangTools

builder_method = j.builder.system.builder_method
ETCD_CONFIG = """
name: "etcd_builder"
data-dir: "/mnt/data"
listen-peer-urls: "http://0.0.0.0:2380"
listen-client-urls: "http://0.0.0.0:2379"
initial-advertise-peer-urls: "http://'$node_addr':2380"
"""


class BuilderEtcd(BuilderGolangTools):
    NAME = "etcd"

    def _init(self):
        super()._init()
        self.package_path = self.package_path_get("etcd", host="go.etcd.io")

    @builder_method()
    def build(self):
        """
        Build etcd
        """
        j.builder.runtimes.golang.install()
        # get a vendored etcd from master
        self.get("go.etcd.io/etcd", install=False, update=False)
        # go to package path and build (for etcdctl)
        self._execute("cd %s && ./build" % self.package_path)

    @builder_method()
    def install(self):

        self.build()
        etcd_bin_path = self.tools.joinpaths(self.package_path, "bin")

        j.builder.tools.dir_ensure(etcd_bin_path)
        j.builder.tools.file_copy("%s/etcd" % etcd_bin_path, "{DIR_BIN}/etcd")
        j.builder.tools.file_copy("%s/etcdctl" % etcd_bin_path, "{DIR_BIN}/etcdctl")

        self._write("/sandbox/cfg/etcd.conf", ETCD_CONFIG)

    @property
    def startup_cmds(self):
        cmd = """
        etcdctl  user add root:root
        etcdctl  auth enable
        etcdctl  --user=root:root put "traefik/acme/account" "foo"
        etcd -conf /sandbox/cfg/etcd.conf
        """
        cmds = [j.tools.startupcmd.get(name="etcd", cmd=cmd)]

        return cmds

    def sandbox(self, create_flist=False, zhub_instance=None):
        """Copy built bins to dest_path and create flist if create_flist = True

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

        self._done_set("sandbox")

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
