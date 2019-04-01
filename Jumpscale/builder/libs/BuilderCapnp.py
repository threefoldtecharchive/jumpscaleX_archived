from Jumpscale import j

JSBASE = j.builder.system._BaseClass

builder_method = j.builder.system.builder_method

class BuilderCapnp(j.builder.system._BaseClass):

    def _init(self):

        self.DIR_BUILD = j.core.tools.text_replace("{DIR_VAR}/build/capnp")
        j.sal.fs.createDir(self.DIR_BUILD)

    @builder_method()
    def build(self):
        """
        install capnp

        kosmos 'j.builder.libs.capnp.build(reset=True)'
        kosmos 'j.builder.libs.capnp.build()'

        """

        # self.prefab.system.package.mdupdate()
        j.builder.buildenv.install()
        if self.tools.isUbuntu:
            j.builder.system.package.ensure('g++')

        # url = "https://capnproto.org/capnproto-c++-0.6.1.tar.gz"
        url = "https://capnproto.org/capnproto-c++-0.7.0.tar.gz"
        self.tools.file_download(url, to=self.DIR_BUILD, overwrite=False, retry=3,
                                       expand=True, minsizekb=900, removeTopDir=True, deletedest=True)

        self.profile_builder_select()

        script = """
        ./configure
        make -j6 check
        make install
        """
        self._execute(script)


    @builder_method()
    def install(self):
        """
        install capnp

        kosmos 'j.builder.libs.capnp.install()'
        """

        self.build()
        self.prefab.runtimes.pip.multiInstall(['cython', 'setuptools', 'pycapnp'], upgrade=True)

        self._done_set('capnp')

    def test(self):
        """
        kosmos 'j.builder.builder.libs.capnp.test()'
        """
        self.build()

        raise RuntimeError("implement")

        print("TEST OK")
