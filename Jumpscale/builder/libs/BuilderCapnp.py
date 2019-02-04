from Jumpscale import j

JSBASE = j.builder.system._BaseClass


class BuilderCapnp(j.builder.system._BaseClass):


    def __init(self):


    def build(self, reset=False):
        """
        install capnp

        js_shell 'j.builder.libs.capnp.build(reset=True)'

        """

        if self._done_get('capnp') and not reset:
            return

        # self.prefab.system.package.mdupdate()
        j.builder.buildenv.install()
        if self.prefab.core.isUbuntu:
            j.builder.tools.package_install('g++')

        url="https://capnproto.org/capnproto-c++-0.6.1.tar.gz"
        dest = j.core.tools.text_replace("{DIR_VAR}/build/capnproto")
        j.sal.fs.createDir(dest)
        self.prefab.core.file_download(url, to=dest, overwrite=False, retry=3,
                    expand=True, minsizekb=900, removeTopDir=True, deletedest=True)

        script = """
        cd {DIR_VAR}/build/capnproto
        ./configure
        make -j6 check
        make install
        """
        j.sal.process.execute(script)

        self._done_set('capnp')


    def install(self):
        self.build()
        self.prefab.runtimes.pip.multiInstall(['cython', 'setuptools', 'pycapnp'], upgrade=True)


        self._done_set('capnp')


    def test(self, build=False):
        """
        js_shell 'j.builder.buildenv(build=True)'
        """
        if build:
            self.build()

        raise RuntimeError("implement")

        print("TEST OK")
