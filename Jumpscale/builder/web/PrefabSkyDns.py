from Jumpscale import j



class BuilderSkyDns(j.builder.system._BaseClass):

    def build(self, start=True, install=True):
        if self.isInstalled():
            return
        j.builder.runtimes.golang.install()
        j.builder.runtimes.golang.get("github.com/skynetservices/skydns")
        if install:
            self.install(start)

    def install(self, start=True):
        """
        download , install, move files to appropriate places, and create relavent configs
        """
        j.builder.tools.file_copy(j.builder.tools.joinpaths('{DIR_BASE}/go', 'bin', 'skydns'), '{DIR_BIN}')
        j.builder.sandbox.addPath(j.core.tools.text_replace("{DIR_BIN}"))

        if start:
            self.start()

    def start(self):
        cmd = j.builder.sandbox.cmdGetPath("skydns")
        pm = j.builder.system.processmanager.get()
        pm.ensure("skydns", cmd + " -addr 0.0.0.0:53")
