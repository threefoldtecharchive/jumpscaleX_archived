from Jumpscale import j


class BuildersTFMUX(j.builders.system._BaseClass):
    def build(self, reset=False):
        """

        kosmos 'j.builders.systemtools.tfmux.build()'

        """

        if reset:
            self.reset()

        if self._done_get("build") and not reset:
            return

        j.builders.system.package.ensure("gcc,g++,make")

        j.builders.system.package.ensure(
            "cmake, g++ pkg-config, git, vim-common, libwebsockets-dev, libjson-c-dev, libssl-dev"
        )

        path = j.clients.git.getContentPathFromURLorPath("https://github.com/threefoldtech/tfmux")

        C = """
        set -xe
        cd {PATH} 
        mkdir -p build
        cd build
        cmake ..
        make
        make install
        """
        self.tools.execute(C, args={"PATH": path})

        self._done_set("build")
