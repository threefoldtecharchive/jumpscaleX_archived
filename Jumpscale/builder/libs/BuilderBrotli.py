from Jumpscale import j




class BuilderBrotli(j.builder.system._BaseClass):

    NAME = 'brotli'

    def _init(self):
        self.src_dir = "{DIR_TEMP}/brotli"

    def build(self, reset=False):
        if reset is False and (self.isInstalled() or self._done_get('build')):
            return
        cmake = j.builder.libs.cmake
        if not cmake.isInstalled():
            cmake.install()
        git_url = "https://github.com/google/brotli.git"
        j.clients.git.pullGitRepo(git_url, dest=self.src_dir, branch='master', depth=1, ssh=False)
        cmd = """
        cd {}
        mkdir out && cd out
        ../configure-cmake
        make
        make test
        """.format(self.src_dir)
        cmd = j.core.tools.text_replace(cmd)
        j.sal.process.execute(cmd)
        self._done_set('build')

    def install(self, reset=False):
        if reset is False and self.isInstalled():
            self._log_info("Brotli already installed")
            return
        if not self._done_get('build'):
            self.build()
        cmd = """
        cd {}/out
        make install
        """.format(self.src_dir)
        j.sal.process.execute(cmd)
        j.builder.system.python_pip.install('brotli>=0.5.2')
