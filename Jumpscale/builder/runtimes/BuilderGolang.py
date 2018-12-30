
from Jumpscale import j
# import os





class BuilderGolang(j.builder.system._BaseClass):

    NAME = 'go'

    def reset(self):
        if #j.builder.sandbox.profileDefault.envExists("GOPATH"):
            go_path = #j.builder.sandbox.profileDefault.envGet("GOPATH")
            #j.builder.sandbox.profileDefault.pathDelete(go_path)
        if #j.builder.sandbox.profileDefault.envExists("GOROOT"):
            go_root = #j.builder.sandbox.profileDefault.envGet("GOROOT")
            #j.builder.sandbox.profileDefault.pathDelete(go_root)
            #j.builder.sandbox.profileJS.pathDelete(go_root)

        #j.builder.sandbox.profileDefault.deleteAll("GOPATH")
        #j.builder.sandbox.profileJS.deleteAll("GOPATH")

        #j.builder.sandbox.profileDefault.deleteAll("GOROOT")
        #j.builder.sandbox.profileJS.deleteAll("GOROOT")

        #j.builder.sandbox.profileDefault.deleteAll("GOGITSDIR")
        #j.builder.sandbox.profileJS.deleteAll("GOGITSDIR")

        #j.builder.sandbox.profileDefault.pathDelete("/go/")
        #j.builder.sandbox.profileJS.pathDelete("/go/")

        # ALWAYS SAVE THE DEFAULT FIRST !!!
        #j.builder.sandbox.profileDefault.save()
        #j.builder.sandbox.profileJS.save()

        self._init()

    def _init(self):
        self.GOROOTDIR = self.replace("{DIR_BASE}") + "/go"
        self.GOPATHDIR = self.replace("{DIR_BASE}") + "/go_proj"
        self.GOPATH = self.GOPATHDIR  # backwards compatibility

    def isInstalled(self):
        rc, out, err = j.sal.process.execute(
            "go version", die=False, showout=False, profile=True)
        if rc > 0 or "1.9" not in out:
            return False
        if self._done_get("install") == False:
            return False
        return True

    def install(self, reset=False, old=False):
        if reset is False and self.isInstalled():
            return
        if j.core.platformtype.myplatform.isMac:
            j.builder.system.package.remove("golang")
            if old is False:
                downl= "https://storage.googleapis.com/golang/go1.10.darwin-amd64.tar.gz"
            else:
                downl = "https://storage.googleapis.com/golang/go1.8.7.darwin-amd64.tar.gz"
        elif "ubuntu" in self.prefab.platformtype.platformtypes:
            if old is False:
                downl = "https://storage.googleapis.com/golang/go1.11.1.linux-amd64.tar.gz"
            else:
                downl = "https://storage.googleapis.com/golang/go1.8.7.linux-amd64.tar.gz"
        else:
            raise j.exceptions.RuntimeError("platform not supported")

        j.sal.process.execute(cmd=j.core.tools.text_replace("rm -rf $GOROOTDIR"), die=True)
        j.core.tools.dir_ensure(self.GOROOTDIR)
        j.core.tools.dir_ensure(self.GOPATHDIR)

        profile = #j.builder.sandbox.profileDefault
        profile.envSet("GOROOT", self.GOROOTDIR)
        profile.envSet("GOPATH", self.GOPATHDIR)
        profile.addPath(j.builder.tools.joinpaths(self.GOPATHDIR, 'bin'))
        profile.addPath(j.builder.tools.joinpaths(self.GOROOTDIR, 'bin'))
        profile.save()

        j.builder.tools.file_download(downl, self.GOROOTDIR, overwrite=False, retry=3,
                                       timeout=0, expand=True, removeTopDir=True)

        j.core.tools.dir_ensure("%s/src" % self.GOPATHDIR)
        j.core.tools.dir_ensure("%s/pkg" % self.GOPATHDIR)
        j.core.tools.dir_ensure("%s/bin" % self.GOPATHDIR)

        self.get("github.com/tools/godep")
        self._done_set("install")

    def goraml(self, reset=False):
        """
        Install (using go get) goraml.
        """
        if reset is False and self._done_get('goraml'):
            return

        self.install()
        self.bindata(reset=reset)

        C = '''
        go get -u github.com/tools/godep
        go get -u github.com/jteeuwen/go-bindata/...
        go get -u github.com/Jumpscale/go-raml
        set -ex
        cd $GOPATH/src/github.com/Jumpscale/go-raml
        sh build.sh
        '''
        j.sal.process.execute(C, profile=True)
        self._done_set('goraml')

    def bindata(self, reset=False):
        """
        Install (using go get) go-bindata.
        """
        if reset is False and self._done_get('bindata'):
            return
        C = '''
        set -ex
        go get -u github.com/jteeuwen/go-bindata/...
        cd $GOPATH/src/github.com/jteeuwen/go-bindata/go-bindata
        go build
        go install
        '''
        j.sal.process.execute(C, profile=True)
        self._done_set('bindata')

    def glide(self):
        """
        install glide
        """
        if self._done_get('glide'):
            return
        j.builder.tools.file_download(
            'https://glide.sh/get', '{DIR_TEMP}/installglide.sh', minsizekb=4)
        j.sal.process.execute('. {DIR_TEMP}/installglide.sh', profile=True)
        self._done_set('glide')

    def clean_src_path(self):
        srcpath = j.builder.tools.joinpaths(self.GOPATHDIR, 'src')
        j.builder.tools.dir_remove(srcpath)

    def get(self, url, install=True, update=True, die=True):
        """
        @param url ,, str url to run the go get command on.
        @param install ,, bool will default build and install the repo if false will only get the repo.
        @param update ,, bool will if True will update requirements if they exist.
        e.g. url=github.com/tools/godep
        """
        self.clean_src_path()
        download_flag = ''
        update_flag = ''
        if not install:
            download_flag = '-d'
        if update:
            update_flag = '-u'
        j.sal.process.execute('go get %s -v %s %s' % (download_flag, update_flag, url),
                             profile=True, die=die)

    def godep(self, url, branch=None, depth=1):
        """
        @param url ,, str url to run the godep command on.
        @param branch ,,str branch to use on the specified repo
        @param depth ,,int depth of repo pull defines how shallow the git clone is
        e.g. url=github.com/tools/godep
        """
        self.clean_src_path()
        GOPATH = self.GOPATH

        pullurl = "git@%s.git" % url.replace('/', ':', 1)

        dest = j.clients.git.pullGitRepo(pullurl,
                                              branch=branch,
                                              depth=depth,
                                              dest='%s/src/%s' % (GOPATH, url),
                                              ssh=False)
        j.sal.process.execute('cd %s && godep restore' % dest, profile=True)
