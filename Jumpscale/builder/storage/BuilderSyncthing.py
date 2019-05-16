from Jumpscale import j
from Jumpscale.builder.runtimes.BuilderGolang import BuilderGolangTools

builder_method = j.builder.system.builder_method
import xml.etree.ElementTree as etree


class BuilderSyncthing(BuilderGolangTools):

    NAME = "syncthing"

    def _init(self):
        super()._init()
        # isolate GOPATH, some dependences conflict with other builders
        self.DIR_GO_PATH = self._replace("{DIR_BUILD}/go_proj")
        self.package_path = self.package_path_get("syncthing", host="github.com/syncthing")

    def profile_builder_set(self):
        self.update_profile_paths(self.profile)

    @builder_method()
    def build(self, version=None):
        """
        build and setup syncthing to run on :8384 , this can be changed from the config file in /optvar/cfg/syncthing
        version e.g. 'v0.14.5'
        """
        j.builder.runtimes.golang.install()
        self.get("github.com/syncthing/syncthing/...", install=False, update=True)

        if version is not None:
            self._execute("cd %s && go run build.go -version %s -no-upgrade" % (self.package_path, version))
        else:
            self._execute("cd %s && go run build.go" % self.package_path)

    @builder_method()
    def install(self, start=True, reset=False, homedir=""):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        src = "{}/bin/syncthing".format(self.package_path)
        self._copy(src, "{DIR_BIN}")
        if not self.tools.dir_exists("{DIR_CFG}/syncthing"):
            cmd = "{DIR_BIN}/syncthing -generate  {DIR_CFG}/syncthing"
        else:
            cmd = "rm -rf {DIR_CFG}/syncthing; {DIR_BIN}/syncthing -generate  {DIR_CFG}/syncthing"
        self._execute(cmd)

    @builder_method()
    def sandbox(self):
        bin_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox")
        self.tools.dir_ensure(bin_dest)
        self._copy("{DIR_BIN}/bin/syncthing", bin_dest)

    @builder_method()
    def clean(self):
        self._remove(self.package_path)
        self._remove(self.DIR_SANDBOX)

    @property
    def startup_cmds(self):
        cmd = self._replace("{DIR_BIN}/syncthing -home  {DIR_CFG}/syncthing")
        cmds = [j.tools.startupcmd.get(name=self.NAME, cmd=cmd)]
        return cmds

    @builder_method()
    def test(self):
        # trying to get syncthing id from api and compare it with the one in config files
        if self.running():
            self.stop()

        self.start()
        sync_client = j.clients.syncthing.get("test", port=8384, addr="localhost", apikey=self.apikey)
        status = sync_client.status_get()
        device_id = status["myID"]
        assert device_id == self.myid
        self.stop()

        print("TEST OK")

    @property
    def apikey(self):
        tree = etree.parse(self._replace("{DIR_CFG}/syncthing/config.xml"))
        root = tree.getroot()
        gui = root.find("gui")
        apikey = gui.find("apikey")
        return apikey.text

    @property
    def myid(self):
        tree = etree.parse(self._replace("{DIR_CFG}/syncthing/config.xml"))
        root = tree.getroot()
        device = root.find("device")
        device_id = device.get("id")
        return device_id
