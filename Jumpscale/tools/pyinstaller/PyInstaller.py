from Jumpscale import j
import imp

JSBASE = j.application.JSBaseClass


class PyInstaller(j.application.JSBaseClass):
    """
    """

    __jslocation__ = "j.tools.pyinstaller"

    def _init(self, **kwargs):
        pass

    def install(self):
        """
        kosmos 'j.tools.pyinstaller.install()'
        :return:
        """

        j.shell()

    def build_jsx(self):
        j.shell()
