from Jumpscale import j
import textwrap

builder_method = j.builders.system.builder_method


class BuilderSonic(j.builders.system._BaseClass):
    NAME = "sonic"

    @builder_method()
    def _init(self):
        pass

    @builder_method()
    def build(self, reset=False):
        j.builders.runtimes.rust.build(reset=reset)
        self.system.package.install("clang")
        self.profile.env_set_part("PATH", j.builders.runtimes.rust.DIR_BUILD)
        self._execute("rustup update")
        self._execute("cargo install sonic-server --force")

    @builder_method()
    def install(self, reset=False):
        j.builders.runtimes.rust.install(reset=reset)

    @builder_method()
    def sandbox(self):
        #TODO: copy sonic bin from bin_dir to sandbox_dir
        pass