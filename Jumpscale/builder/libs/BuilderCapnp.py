from Jumpscale import j

JSBASE = j.builder.system._BaseClass

builder_method = j.builder.system.builder_method

class BuilderCapnp(JSBASE):
    NAME = "capnp"

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
        self.tools.file_download(url, to="{}/capnproto".format(self.DIR_BUILD), overwrite=False, retry=3,
                                       expand=True, minsizekb=900, removeTopDir=True, deletedest=True)

        self.profile_builder_select()

        script = """
        cd {DIR_BUILD}
        ./configure CXXFLAGS="-DHOLES_NOT_SUPPORTED"
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
        if self.tools.isUbuntu:
            j.builder.system.package.ensure('g++')
        j.builder.runtimes.python.pip_package_install(['cython', 'setuptools', 'pycapnp'])

    def test(self):
        """
        kosmos 'j.builder.builder.libs.capnp.test()'
        """
        self.build()

        raise RuntimeError("implement")

        print("TEST OK")
