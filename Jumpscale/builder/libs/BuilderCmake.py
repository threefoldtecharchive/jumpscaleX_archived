from Jumpscale import j




class BuilderCmake(j.builder.system._BaseClass):
    NAME = 'cmake'

    def _init(self):
        self.src_dir = "{DIR_TEMP}/cmake"

    def build(self):
        j.builder.tools.dir_ensure(self.src_dir)
        cmake_url = "https://cmake.org/files/v3.8/cmake-3.8.2.tar.gz"
        j.builder.tools.file_download(cmake_url, to=self.src_dir, overwrite=False, expand=True, removeTopDir=True)
        cmd = """
        cd %s && ./bootstrap && make
        """ % self.src_dir
        j.sal.process.execute(cmd)
        self._done_set('build')
        return

    def install(self):
        if self.isInstalled():
            return
        if not self._done_get('build'):
            self.build()
        cmd = """
        cd %s && make install
        """ % self.src_dir
        j.sal.process.execute(cmd)
        return
