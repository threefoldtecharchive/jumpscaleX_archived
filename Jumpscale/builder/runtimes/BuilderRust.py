from Jumpscale import j

builder_method = j.builder.system.builder_method


class BuilderRust(j.builder.system._BaseClass):
    NAME = "rust"
    DOWNLOAD_URL = "https://sh.rustup.rs"

    def _init(self):
        self.DIR_BUILD = self._replace("{DIR_VAR}/build/rust")

    @builder_method()
    def install(self):
        self.profile_sandbox_select()

        # Will download and run the correct version of rustup-init executable for your platform
        self._execute(
            "curl {} -sSf | sh -s -- -y".format(self.DOWNLOAD_URL)
        )
        self._execute("source $HOME/.cargo/env")
        self._execute("echo  'export PATH='$HOME/.cargo/bin:$PATH'' >> ~/.bashrc ")

