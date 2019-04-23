from Jumpscale import j
import textwrap
from .BuilderDigitalME import BuilderDigitalME

builder_method = j.builder.system.builder_method


class BuilderUserBot(j.builder.system._BaseClass):
    """
    specs:

        - build all required components (only work on ub 1804) using self.build
        - sandbox to sandbox dir
        - create flist
        - in self.test_zos() start the created flist & do the network tests for the openresty

    """
    NAME = "userbot"

    @builder_method()
    def _init(self):
        pass

    @builder_method()
    def build(self, reset=False):
        """
        kosmos 'j.tools.sandboxer.sandbox_build()'

        will build python & openresty & copy all to the right git sandboxes works for Ubuntu only
        :return:
        """
        j.builder.apps.digitalme.build(reset=reset)
        j.builder.db.zdb.build(reset=reset)

    @builder_method()
    def install(self):
        """
        Installs the zdb binary to the correct location
        """
        j.builder.db.zdb.install()

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=True, merge_base_flist="tf-autobuilder/threefoldtech-jumpscaleX-autostart-development.flist"):
        import ipdb; ipdb.set_trace()
        j.builder.apps.digitalme.sandbox(reset=True)
        j.tools.sandboxer.copyTo(j.builder.apps.digitalme.DIR_SANDBOX, self.DIR_SANDBOX)

        j.builder.db.zdb.sandbox(reset=True)
        j.tools.sandboxer.copyTo(j.builder.db.zdb.DIR_SANDBOX,  self.DIR_SANDBOX)

        startup_file = self.tools.joinpaths(j.sal.fs.getDirName(__file__), 'templates', 'bot_startup.toml')
        file_dest = self.tools.joinpaths(self.DIR_SANDBOX, '.startup.toml')
        self._copy(startup_file, file_dest)

        startup_file = self.tools.joinpaths(j.sal.fs.getDirName(__file__), 'templates', 'userbot_startup.sh')
        file_dest = self.tools.joinpaths(self.DIR_SANDBOX, 'bot_startup.sh')
        self._copy(startup_file, file_dest)


