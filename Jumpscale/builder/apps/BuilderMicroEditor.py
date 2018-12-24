from Jumpscale import j
import os
import textwrap


class BuilderMicroEditor(j.builder.system._BaseClass):
    NAME = "micro"

    def install(self, reset=False):
        """
        """

        if self._done_check("install", reset):
            return

        print("INSTALL MICROEDITOR")

        if j.builder.tools.isMac:
            url = "https://github.com/zyedidia/micro/releases/download/v1.3.3/micro-1.3.3-osx.tar.gz"
        elif j.builder.tools.isUbuntu:
            url = "https://github.com/zyedidia/micro/releases/download/v1.3.3/micro-1.3.3-linux64.tar.gz"
        else:
            raise RuntimeError("not implemented for other platforms")

        dest = j.builder.network.tools.download(
            url=url, to='{DIR_TEMP}/micro/', overwrite=False, retry=3, expand=True, removeTopDir=True)
        j.builder.tools.file_move("{DIR_TEMP}/micro/micro",
                            "/usr/local/bin/micro", recursive=False)

        self._done_set('install')
