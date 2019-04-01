from Jumpscale import j

builder_method = j.builder.system.builder_method


class BuilderOpenSSL(j.builder.system._BaseClass):

    NAME = "openssl"


    def __init__(self):
        self.CODEDIRL = j.core.tools.text_replace("{DIR_VAR}/build/code/openssl")
        if j.core.platformtype.myplatform.isMac:
            self.TARGET = "darwin64-x86_64-cc"
        else:
            self.TARGET = "linux-generic64"

        j.builder.system._BaseClass.__init__(self)

    @builder_method()
    def _init(self):
        pass


    @builder_method()
    def install(self):
        raise RuntimeError("implement")

    @builder_method()
    def reset(self):
        self._remove("{BUILDDIRL}")
        self._remove("{CODEDIRL}")

    @builder_method()
    def build(self, reset=False):
        """
        js_shell 'j.builder.libs..openssl.build()'
        """
        if not self.tools.dir_exists(self._replace("{CODEDIRL}/openssl")):
            self._execute("""
            cd {CODEDIRL}
            git clone https://github.com/openssl/openssl.git
            """)

        C = """
        set -ex
        mkdir -p {DIR_BUILD}
        cd {CODEDIRL}
        ./config
        ./Configure {TARGET} shared enable-ec_nistp_64_gcc_128 no-ssl2 no-ssl3 no-comp --openssldir={DIR_BUILD}\
         --prefix={DIR_BUILD}
        make depend
        make install
        rm -rf {DIR_BUILD}/share
        rm -rf {DIR_BUILD}/build/private
        echo "**BUILD DONE**"
        """
        self._write("{CODEDIRL}/mycompile_all.sh", C)
        self._execute("cd {CODEDIRL}; sh ./mycompile_all.sh")


    def test(self, build=False):
        """
        js_shell 'j.builder.buildenv(build=True)'
        """
        if build:
            self.build()

        raise RuntimeError("implement")

        print("TEST OK")
