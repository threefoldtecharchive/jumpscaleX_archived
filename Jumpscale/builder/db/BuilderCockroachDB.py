from Jumpscale import j



class BuilderCockroachDB(j.builder.system._BaseClass):
    NAME = 'cockroachdb'

    def install(self, start=True, reset=False):
        """
        download, install, move files to appropriate places, and create relavent configs
        """
        if self._done_check("install", reset):
            return

        appbase = "%s/" % j.builder.tools.dir_paths["BINDIR"]
        j.core.tools.dir_ensure(appbase)

        url = 'https://binaries.cockroachdb.com/cockroach-latest.linux-amd64.tgz'
        dest = "{DIR_TEMP}/cockroach-latest.linux-amd64"

        self._logger.info('Downloading CockroachDB.')
        j.builder.tools.file_download(
            url, to="{DIR_TEMP}", overwrite=False, expand=True)
        tarpaths = j.builder.tools.find(
            "{DIR_TEMP}", recursive=False, pattern="*cockroach*.tgz", type='f')
        if len(tarpaths) == 0:
            raise j.exceptions.Input(message="could not download:%s, did not find in %s" % (url, j.core.tools.text_replace("{DIR_TEMP}")))
        tarpath = tarpaths[0]
        j.builder.tools.file_expand(tarpath, "{DIR_TEMP}")

        for file in j.builder.tools.find(dest, type='f'):
            j.builder.tools.file_copy(file, appbase)
        self._done_set("install")
        if start:
            self.start(reset=reset)

    def build(self, start=True, reset=False):
        raise RuntimeError("not implemented")

    def start(self, host="localhost", insecure=True, background=False, reset=False, port=26257, http_port=8581):
        if self.isStarted() and not reset:
            return
        cmd = "{DIR_BIN}/cockroach start --host=%s" % host
        if insecure:
            cmd = "%s --insecure" % (cmd)
        if background:
            cmd = "%s --background" % (cmd)
        cmd = "%s --port=%s --http-port=%s" % (cmd, port, http_port)

        # cmd = "{DIR_BIN}/cockroach start --insecure --host=localhost --background"
        j.builder.system.process.kill("cockroach")
        pm = j.builder.system.processmanager.get()
        pm.ensure(name="cockroach", cmd=cmd, env={}, path="", autostart=True)

    def stop(self):
        pm = j.builder.system.processmanager.get()
        pm.stop("cockroach")
