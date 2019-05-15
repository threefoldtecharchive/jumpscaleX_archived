from Jumpscale import j
builder_method = j.builder.system.builder_method


class BuilderCmake(j.builder.system._BaseClass):
    NAME = 'cmake'

    def _init(self):
        self.package_path = self._replace("{DIR_TEMP}/CMake")

    @builder_method()
    def build(self):
        cmake_url = 'https://github.com/Kitware/CMake'
        j.clients.git.pullGitRepo(url=cmake_url, dest=self.package_path, depth=1)
        cmd = """
        cd {}
        ./bootstrap && make && make install
        """.format(self.package_path)
        self._execute(cmd)

    @builder_method()
    def install(self):
        self.src = '{}/bin/'.format(self.package_path)
        self._copy(self.src, '{DIR_BIN}')

    @builder_method()
    def sandbox(self, zhub_client=None, flist_create=True, merge_base_flist='tf-autobuilder/threefoldtech-jumpscaleX-development.flist'):
        bins = ['cmake', 'cpack', 'ctest']
        for bin_name in bins:
            dir_src = self.tools.joinpaths(j.dirs.BINDIR, bin_name)
            dir_dest = self.tools.joinpaths(self.DIR_SANDBOX, j.dirs.BINDIR[1:])
            self.tools.dir_ensure(dir_dest)
            self._copy(dir_src, dir_dest)
        
        lib_dest = self.tools.joinpaths(self.DIR_SANDBOX, 'sandbox/lib')
        self.tools.dir_ensure(lib_dest)
        for bin in bins:
            dir_src = self.tools.joinpaths(j.dirs.BINDIR, bin)
            j.tools.sandboxer.libs_sandbox(dir_src, lib_dest, exclude_sys_libs=False)

    def clean(self):
        self._remove(self.package_path)

    def test(self):
        path = self._execute('which cmake', showout=False)
        assert path[1].strip() == '/sandbox/bin/cmake'
        print('TEST OK')
