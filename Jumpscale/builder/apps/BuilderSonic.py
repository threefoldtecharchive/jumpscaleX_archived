from Jumpscale import j
import textwrap

builder_method = j.builders.system.builder_method


class BuilderSonic(j.builders.system._BaseClass):
    NAME = "sonic"

    @builder_method()
    def _init(self, **kwargs):
        pass

    @builder_method()
    def build(self, reset=False):
        """
        kosmos  'j.builders.apps.sonic.build()'
        :param reset:
        :return:
        """

        j.builders.runtimes.rust.install()

        if not j.core.platformtype.myplatform.platform_is_osx:
            self.system.package.install("clang")
        self.profile.env_set_part("PATH", j.builders.runtimes.rust.DIR_CARGOBIN)
        self._execute("rustup update")
        if reset:
            self._execute("cargo install sonic-server --force")
        else:
            self._execute("cargo install sonic-server")

    @builder_method()
    def install(self, reset=False):
        """
        kosmos  'j.builders.apps.sonic.install()'
        :param reset:
        :return:
        """
        self._execute("cp %s/sonic /sandbox/bin/" % j.builders.runtimes.rust.DIR_CARGOBIN)
