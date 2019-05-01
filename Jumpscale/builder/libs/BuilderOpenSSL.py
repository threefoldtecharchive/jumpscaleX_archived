from Jumpscale import j

builder_method = j.builder.system.builder_method


class BuilderOpenSSL(j.builder.system._BaseClass):

    NAME = "openssl"

    def __init__(self):
        if j.core.platformtype.myplatform.isMac:
            self.TARGET = "darwin64-x86_64-cc"
        else:
            self.TARGET = "linux-generic64"

        j.builder.system._BaseClass.__init__(self)

    @builder_method()
    def reset(self):
        self._remove("{DIR_BUILD}")

    @builder_method()
    def build(self, reset=False):
        """
        js_shell 'j.builder.libs..openssl.build()'
        """
        if not self.tools.exists(self.DIR_BUILD):
            C = """
            set -ex
            cd {DIR_BUILD}
            git clone --depth 1 https://github.com/openssl/openssl.git
            """
            self._execute(C)

        C = """
        cd {DIR_BUILD}/openssl
        ./config -Wl,--enable-new-dtags,-rpath,'$(LIBRPATH)'
        ./Configure {TARGET} shared enable-ec_nistp_64_gcc_128 no-ssl2 no-ssl3 no-comp --openssldir=/sandbox/var/openssl --prefix=/sandbox/ zlib
        make depend
        make install
        rm -rf /sandbox/share
        rm -rf /sandbox/build/private
        echo "**BUILD DONE**"
        """
        self.tools.dir_ensure("{DIR_BUILD}")
        self._write("{DIR_BUILD}/mycompile_all.sh", C)
        self._execute("cd {DIR_BUILD}; sh ./mycompile_all.sh")

    def test(self, build=False):
        """
        js_shell 'j.builder.buildenv(build=True)'
        """
        if build:
            self.build()

        raise RuntimeError("implement")

        print("TEST OK")
