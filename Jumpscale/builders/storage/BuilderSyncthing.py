from Jumpscale import j




class BuilderSyncthing(j.builder.system._BaseClass):

    NAME = 'syncthing'

    @property
    def builddir(self):
        return j.builder.core.dir_paths['BUILDDIR'] + "/syncthing"

    def build(self, start=True, install=True, reset=False, version='v0.14.18'):
        """
        build and setup syncthing to run on :8384 , this can be changed from the config file in /optvar/cfg/syncthing
        version e.g. 'v0.14.5'
        """

        if self.doneGet("build") and not reset:
            return

        j.builder.runtimes.golang.install()

        # build
        url = "https://github.com/syncthing/syncthing.git"
        if j.builder.core.file_exists('{DIR_BASE}/go/src/github.com/syncthing/syncthing'):
            j.builder.core.dir_remove('{DIR_BASE}/go/src/github.com/syncthing/syncthing')
        dest = j.clients.git.pullGitRepo(url,
                                                     dest='{DIR_BASE}/go/src/github.com/syncthing/syncthing',
                                                     ssh=False,
                                                     depth=1)

        if version is not None:
            j.sal.process.execute("cd %s && go run build.go -version %s -no-upgrade" % (dest, version), profile=True)
        else:
            j.sal.process.execute("cd %s && go run build.go" % dest, profile=True)

        # j.builder.core.dir_ensure(self.builddir+"/cfg")
        # j.builder.core.dir_ensure(self.builddir+"/bin")

        j.builder.core.copyTree(
            '{DIR_BASE}/go/src/github.com/syncthing/syncthing/bin',
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

        self.doneSet("build")

        if install:
            self.install(start=start)

    def install(self, start=True, reset=False, homedir=""):
        """
        download, install, move files to appropriate places, and create relavent configs
        """

        if self.doneGet("install") and not reset:
            return

        self.build()
        j.builder.system.python_pip.install("syncthing")

        j.builder.core.dir_ensure("$CFGDIR/syncthing")
        # j.sal.fs.writeFile("$CFGDIR/syncthing/syncthing.xml", config)

        j.builder.core.copyTree(self.builddir + "/bin", "{DIR_BIN}")

        self.doneSet("install")

        if start:
            self.start()

    def start(self, reset=False):

        if reset:
            j.sal.process.execute("killall syncthing", die=False)
            j.sal.process.execute("rm -rf $CFGDIR/syncthing")

        if j.builder.core.dir_exists("$CFGDIR/syncthing") == False:
            j.sal.process.execute(cmd="rm -rf $CFGDIR/syncthing;cd {DIR_BIN};./syncthing -generate  $CFGDIR/syncthing")
        pm = j.builder.system.processmanager.get("tmux")
        pm.ensure(name="syncthing", cmd="./syncthing -home  $CFGDIR/syncthing", path="{DIR_BIN}")

    @property
    def apikey(self):
        import xml.etree.ElementTree as etree
        tree = etree.parse(j.core.tools.text_replace("$CFGDIR/syncthing/config.xml"))
        r = tree.getroot()
        for item in r:
            if item.tag == "gui":
                for item2 in item:
                    self._logger.info(item2.tag)
                    if item2.tag == "apikey":
                        return item2.text

    def stop(self):
        pm = j.builder.system.processmanager.get("tmux")
        pm.stop("syncthing")

    def getApiClient(self):
        from IPython import embed
        self._logger.info("DEBUG NOW u8")
        embed()
        raise RuntimeError("stop debug here")
        import syncthing
        sync = syncthing.Syncthing(api_key=self.apikey, host="127.0.0.1", port=8384)
        sync.sys.config()
        return sync

    def restart(self):
        self.stop()
        self.start()
