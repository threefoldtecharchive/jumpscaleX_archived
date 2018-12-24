from Jumpscale import j
import os
import textwrap



class BuilderDuplicacy(j.builder.system._BaseClass):
    NAME = "duplicacy"

    def build(self, reset=False, install=False):
        """
        Builds duplicacy

        @param reset boolean: forces the build operation.
        """
        if self.doneCheck("build", reset):
            return

        dup_url = "https://github.com/gilbertchen/duplicacy/releases/download/v2.0.10/duplicacy_linux_x64_2.0.10"
        j.builder.core.file_download(dup_url, overwrite=True, to="{DIR_TEMP}/duplicacy")
        self.doneSet('build')

        if install:
            self.install(False)

    def install(self, reset=False, start=False):
        """
        Installs duplicacy

        @param reset boolean: forces the install operation.
        """
        if self.doneCheck("install", reset):
            return
        j.sal.process.execute("cp {DIR_TEMP}/duplicacy {DIR_BIN}/")
        self.doneSet('install')

        if start:
            self.start()

    def start(self, name="main"):
        """
        Starts duplicacy.
        """
        pass


    def stop(self, name='main'):
        """
        Stops duplicacy 
        """

        pass

    def restart(self, name="main"):
        self.stop(name)
        self.start(name)

    def reset(self):
        """
        helper method to clean what this module generates.
        """
        pass

