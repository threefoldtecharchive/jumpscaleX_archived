from Jumpscale import j
import textwrap

builder_method = j.builders.system.builder_method


class BuilderThreebot(j.builders.system._BaseClass):
    NAME = "threebot"

    def _init(self, **kwargs):
        self.BUILD_LOCATION = self._replace("{DIR_BUILD}/threebot")

    @builder_method()
    def install(self, reset=False):
        j.builders.web.openresty.install(reset=reset)
        j.builders.runtimes.lua.install(reset=reset)
        j.builders.db.zdb.install(reset=reset)
        j.builders.apps.sonic.install(reset=reset)

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=True):
        j.builders.runtimes.lua.sandbox(reset=reset)
        j.builders.db.zdb.sandbox(reset=reset)
        j.builders.apps.sonic.sandbox(reset=reset)

        self.tools.copyTree(j.builders.web.openresty.DIR_SANDBOX, self.DIR_SANDBOX)
        self.tools.copyTree(j.builders.runtimes.lua.DIR_SANDBOX, self.DIR_SANDBOX)
        self.tools.copyTree(j.builders.db.zdb.DIR_SANDBOX, self.DIR_SANDBOX)
        self.tools.copyTree(j.builders.apps.sonic.DIR_SANDBOX, self.DIR_SANDBOX)

        file = self.tools.joinpaths(j.sal.fs.getDirName(__file__), "templates", "threebot_startup.toml")
        file_dest = self.tools.joinpaths(self.DIR_SANDBOX, ".startup.toml")
        self._copy(file, file_dest)

        file = self.tools.joinpaths(j.sal.fs.getDirName(__file__), "templates", "3bot_configure.toml")
        file_dest = self.tools.joinpaths(self.DIR_SANDBOX, "3bot_configure.toml")
        self._copy(file, file_dest)

        startup_file = self.tools.joinpaths(j.sal.fs.getDirName(__file__), "templates", "3bot_startup.sh")
        file_dest = self.tools.joinpaths(self.DIR_SANDBOX, "3bot_startup.sh")
        self._copy(startup_file, file_dest)

    def start(self):
        j.servers.threebot.default.start()
        return True

    def stop(self):
        j.servers.threebot.default.stop()
        return True

    @builder_method()
    def test(self):
        assert self.start()
        assert self.stop()

        print("TEST OK")

    @builder_method()
    def clean(self):
        self._remove(self.BUILD_LOCATION)

    @builder_method()
    def reset(self):
        super().reset()
        self.clean()
