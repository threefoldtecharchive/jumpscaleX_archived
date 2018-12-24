from Jumpscale import j
import os
import textwrap



class BuilderMinio(j.builder.system._BaseClass):
    NAME = "minio"

    def _init(self):
        self.BUILDDIR = j.core.tools.text_replace("{DIR_TEMP}/minio")

    def build(self, reset=False, install=False):
        """
        Builds minio

        @param reset boolean: forces the build operation.
        """
        if self.doneCheck("build", reset):
            return
        j.builder.core.dir_ensure(self.BUILDDIR)

        minio_url = "https://dl.minio.io/server/minio/release/linux-amd64/minio"
        j.builder.core.file_download(minio_url, overwrite=True, to=self.BUILDDIR, expand=False, removeTopDir=True)
        self.doneSet('build')

        if install:
            self.install(False)

    def install(self, reset=False, start=False):
        """
        Installs minio

        @param reset boolean: forces the install operation.
        """
        if self.doneCheck("install", reset):
            return
        j.sal.process.execute("cp {DIR_TEMP}/minio {DIR_BIN}/")
        self.doneSet('install')

        if start:
            self.start()

    def start(self, name="main", datadir="/tmp/shared", address="0.0.0.0", port=90000, miniokey="", miniosecret=""):
        """
        Starts minio.
        """
        j.builder.core.dir_ensure(datadir)

        cmd = "MINIO_ACCESS_KEY={} MINIO_SECRET_KEY={} minio server --address {}:{} {}".format(miniokey, miniosecret, address, port, datadir)
        pm = j.builder.system.processmanager.get()
        pm.ensure(name='minio_{}'.format(name), cmd=cmd)


    def stop(self, name='main'):
        """
        Stops minio 
        """

        pm.stop(name='minio_{}'.format(name))


    def restart(self, name="main"):
        self.stop(name)
        self.start(name)

    def reset(self):
        """
        helper method to clean what this module generates.
        """
        pass

