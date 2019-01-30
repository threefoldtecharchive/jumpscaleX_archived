from Jumpscale import j




class BuilderSyncthing(j.builder.system._BaseClass):

    NAME = 'syncthing'

    @property
    def builddir(self):
        return "/tmp/builder/syncthing"

    def build(self, start=True, install=True, reset=False, version='v0.14.18'):
        """
        build and setup syncthing to run on :8384 , this can be changed from the config file in /optvar/cfg/syncthing
        version e.g. 'v0.14.5'
        """

        if self._done_get("build") and not reset:
            return

        j.builder.runtimes.golang.install()

        # build
        url = "https://github.com/syncthing/syncthing.git"
        syncthing_path = j.core.tools.text_replace('{DIR_BASE}/go/src/github.com/syncthing/syncthing')
        if j.builder.tools.file_exists(syncthing_path):
            j.builder.tools.dir_remove(syncthing_path)
        dest = j.clients.git.pullGitRepo(url,
                                     dest=syncthing_path,
                                     ssh=False,
                                     depth=1)

        if version is not None:
            j.builder.tools.run("cd %s && go run build.go -version %s -no-upgrade" % (dest, version))
        else:
            j.builder.tools.run("cd %s && go run build.go" % dest)

        j.builder.tools.copyTree(
            syncthing_path + "/bin",
            self.builddir + "/bin",
            keepsymlinks=False,
            deletefirst=True,
            overwriteFiles=True,
            recursive=True,
            rsyncdelete=True,
            createdir=True,
            ignorefiles=[
                'testutil',
                'stbench'])

        self._done_set("build")

        if install:
            self.install(start=start, reset=reset)

    def install(self, start=True, reset=False, homedir=""):
        """
        download, install, move files to appropriate places, and create relavent configs
        """

        if self._done_get("install") and not reset:
            return

        self.build()
        # j.builder.system.python_pip.install("syncthing")

        j.core.tools.dir_ensure(j.core.tools.text_replace("{DIR_CFG}/syncthing"))
        # j.sal.fs.writeFile("$CFGDIR/syncthing/syncthing.xml", config)

        j.builder.tools.copyTree(self.builddir + "/bin", j.core.tools.text_replace("{DIR_BIN}"))

        self._done_set("install")

        if start:
            self.start()

    def start(self, reset=False):

        if reset:
            j.builder.tools.run("killall syncthing")
            j.builder.tools.run(j.core.tools.text_replace("rm -rf {DIR_CFG}/syncthing"))

        if j.builder.tools.dir_exists(j.core.tools.text_replace("{DIR_CFG}/syncthing")) == False:
            j.builder.tools.run(j.core.tools.text_replace("rm -rf {DIR_CFG}/syncthing;cd {DIR_BIN};./syncthing -generate  {DIR_CFG}/syncthing"))
        cmd = j.tools.tmux.cmd_get(name="syncthing", window="syncthing", cmd=j.core.tools.text_replace("./syncthing -home  {DIR_CFG}/syncthing"), path=j.core.tools.text_replace("{DIR_BIN}"))
        cmd.start()

    @property
    def apikey(self):
        import xml.etree.ElementTree as etree
        tree = etree.parse(j.core.tools.text_replace("{DIR_CFG}/syncthing/config.xml"))
        r = tree.getroot()
        for item in r:
            if item.tag == "gui":
                for item2 in item:
                    self._logger.info(item2.tag)
                    if item2.tag == "apikey":
                        return item2.text

    def stop(self):
        cmd = j.tools.tmux._find_procs_by_name("syncthing")
        cmd.stop()

    def getApiClient(self):
        #TODO : not te be tested
        from syncthing import Syncthing
        sync = Syncthing(api_key=self.apikey, host="127.0.0.1", port=8384)
        sync.sys.config()
        return sync

    def restart(self):
        self.stop()
        self.start()
