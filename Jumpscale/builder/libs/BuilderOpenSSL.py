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
        C = """
        set -ex
        cd {DIR_BUILD}
        git clone https://github.com/openssl/openssl.git
        cd openssl
        ./config
        ./Configure {TARGET} shared enable-ec_nistp_64_gcc_128 no-ssl2 no-ssl3 no-comp --openssldir={DIR_BUILD} --prefix={DIR_BUILD} zlib
        make depend
        make install
        rm -rf {DIR_BUILD}/share
        rm -rf {DIR_BUILD}/build/private
        echo "**BUILD DONE**"
        """
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
