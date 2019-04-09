from Jumpscale import j

builder_method = j.builder.system.builder_method


class BuilderRust(j.builder.system._BaseClass):
    NAME = "rust"
    VERSION = "rust-nightly-x86_64-unknown-linux-gnu"
    DOWNLOAD_URL = "https://static.rust-lang.org/dist/{}.tar.gz".format(VERSION)

    def _init(self):

        self.DIR_BUILD = self._replace("{DIR_VAR}/build/rust")

    @builder_method()
    def build(self):

        self._execute(
            "curl -o {}/rust.tar.gz {}".format(self.DIR_BUILD, self.DOWNLOAD_URL)
        )
        self._execute("tar --overwrite -xf {DIR_BUILD}/rust.tar.gz -C {DIR_BUILD}")

        self._execute(
            "cd /tmp/{} && ./install.sh --prefix={}/apps/rust --destdir=={}/apps/rust".format(
                self.VERSION, self.DIR_BUILD, self.DIR_BUILD
            )
        )

    @builder_method()
    def install(self):

        self.build()
        rust_bin_path = self.tools.joinpaths("{DIR_BUILD}/apps/rust", "bin")

        j.builder.tools.dir_ensure(rust_bin_path)
        self._copy(rust_bin_path, "{DIR_BIN}")

    @builder_method()
    def sandbox(self):
        bin_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox")
        self.tools.dir_ensure(bin_dest)
        self._copy("{DIR_BUILD}/apps/rust/bin", bin_dest)

    @builder_method()
    def test(self):
        self.install()

        rc, _, _ = self._execute("rustfmt -V")
        if rc:
            print("TEST Failed")
            return
        print("TEST DONE")

