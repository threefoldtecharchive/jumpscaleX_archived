from Jumpscale import j



class BuilderAtomicswap(j.builder.system._BaseClass):
    NAME = "atomicswap"

    def build(self, branch=None,tag=None, revision=None, reset=False):
        if self.doneGet('build') and reset is False:
            return
        j.builder.system.package.mdupdate()
        j.builder.tools.package_install("git")
        golang = j.builder.runtimes.golang
        golang.install()
        GOPATH = golang.GOPATH
        url = 'github.com/rivine'
        path = '%s/src/%s/atomicswap' % (GOPATH, url)
        pullurl = 'https://%s/atomicswap.git' % url
        dest = j.clients.git.pullGitRepo(pullurl,
                                              branch=branch,
                                              tag=tag,
                                              revision=revision,
                                              dest=path,
                                              ssh=False)
        cmd = 'cd {} && make install'.format(dest)
        j.sal.process.execute(cmd)

        self.doneSet('build')

    def install(self, branch=None,tag='v0.1.0', revision=None, reset=False):
        # if branch, tag, revision = None it will build form master
        if self.doneGet('install') and reset is False:
            return

        self.build(branch=branch,tag=tag, revision=revision, reset=reset)
        tfchaindpath = j.builder.core.joinpaths(j.builder.runtimes.golang.GOPATH, 'bin', 'btcatomicswap')
        tfchaincpath = j.builder.core.joinpaths(j.builder.runtimes.golang.GOPATH, 'bin', 'ethatomicswap')

        j.builder.core.file_copy(tfchaindpath, "{DIR_BIN}/")
        j.builder.core.file_copy(tfchaincpath, "{DIR_BIN}/")

        self.doneSet('install')
