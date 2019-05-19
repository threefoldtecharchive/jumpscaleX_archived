from Jumpscale import j
import imp

JSBASE = j.application.JSBaseClass


class PyInstaller(j.application.JSBaseClass):
    """
    """

    __jslocation__ = "j.tools.pyinstaller"

    def _init(self):
        pass

    def install(self):
        j.shell()

    def build_kosmos(self):
        j.shell()
