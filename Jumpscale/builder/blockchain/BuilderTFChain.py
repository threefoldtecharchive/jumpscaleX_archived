from Jumpscale import j



class BuilderTFChain(j.builder.system._BaseClass):
    NAME = "tfchain"

    def build(self, branch=None,tag=None, revision=None, reset=False):
        if self._done_get('build') and reset is False:
            return
        j.builder.system.package.mdupdate()
        j.builder.tools.package_install("git")
        golang = j.builder.runtimes.golang
        golang.install()
        GOPATH = golang.GOPATH
        url = 'github.com/threefoldfoundation'
        path = '%s/src/%s/tfchain' % (GOPATH, url)
        pullurl = 'https://%s/tfchain.git' % url
        dest = j.clients.git.pullGitRepo(pullurl,
                                              branch=branch,
                                              tag=tag,
                                              revision=revision,
                                              dest=path,
                                              ssh=False)
        cmd = 'cd {} && make install-std'.format(dest)
        j.sal.process.execute(cmd)

        self._done_set('build')

    def install(self, branch=None,tag=None, revision=None, reset=False):
        # if branch, tag, revision = None it will build form master
        if self._done_get('install') and reset is False:
            return

        self.build(branch=branch,tag=tag, revision=revision, reset=reset)
        tfchaindpath = j.builder.tools.joinpaths(j.builder.runtimes.golang.GOPATH, 'bin', 'tfchaind')
        tfchaincpath = j.builder.tools.joinpaths(j.builder.runtimes.golang.GOPATH, 'bin', 'tfchainc')

        j.builder.tools.file_copy(tfchaindpath, "{DIR_BIN}/")
        j.builder.tools.file_copy(tfchaincpath, "{DIR_BIN}/")

        self._done_set('install')
