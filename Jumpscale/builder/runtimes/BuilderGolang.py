from Jumpscale import j


class BuilderGolang(j.builder.system._BaseClass):

    NAME = 'go'
    STABLE_VERSION = '1.11'
    DOWNLOAD_URL = 'https://dl.google.com/go/go{version}.{platform}-{arch}.tar.gz'

    def reset(self):
        if self.profile_default.envExists("GOROOT"):
            go_root = self.profile_default.envGet("GOROOT")
            self.profile_default.pathDelete(go_root)
            self.profile_js.pathDelete(go_root)
        if self.profile_default.envExists("GOPATH"):
            go_path = self.profile_default.envGet("GOPATH")
            self.profile_default.pathDelete(go_path)

        self.profile_default.deleteAll("GOROOT")
        self.profile_js.deleteAll("GOROOT")
        self.profile_default.deleteAll("GOPATH")
        self.profile_js.deleteAll("GOPATH")

        # ALWAYS SAVE THE DEFAULT FIRST !!!
        self.profile_default.save()
        self.profile_js.save()

    def _init(self):
        self.base_dir = j.core.tools.text_replace('{DIR_BASE}')

        self.tools = j.builder.tools
        self.bash = j.tools.bash.get()
        self.profile_default = self.bash.profileDefault
        self.profile_js = self.bash.profileJS

        self.go_root = self.tools.joinpaths(self.base_dir, 'go')
        self.go_path = self.tools.joinpaths(self.base_dir, 'go_proj')
        self.go_root_bin = self.tools.joinpaths(self.go_root, 'bin')
        self.go_path_bin = self.tools.joinpaths(self.go_path, 'bin')

    @property
    def version(self):
        """gets the current installed go version

        :raises j.exceptions.RuntimeError: in case go is not installed
        :return: go version e.g. 1.11.4
        :rtype: str
        """
        rc, out, err = j.sal.process.execute('go version', die=False, showout=False)
        if rc:
            raise j.exceptions.RuntimeError('go is not instlled\n%s' % err)
        return j.data.regex.findOne(r'go\d+.\d+.\d+', out)[2:]

    @property
    def is_installed(self):
        """checks if go is installed with the latest stable version

        :return: installed and the version is `VERSION_STABLE` or not
        :rtype: bool
        """
        if not self._done_get('install'):
            return False

        try:
            version = self.version
            return self.STABLE_VERSION in version
        except j.exceptions.RuntimeError:
            return False

    def install(self, reset=False):
        """Install go

        :param reset: reset installation, defaults to False
        :param reset: bool, optional
        :raises j.exceptions.RuntimeError: in case the platform is not supported
        """
        if self.is_installed and not reset:
            return

        # only check for linux for now
        if j.core.platformtype.myplatform.is32bit:
            arch = '386'
        else:
            arch = 'amd64'

        if j.core.platformtype.myplatform.isLinux:
            download_url = self.DOWNLOAD_URL.format(version='1.11.4', platform='linux', arch=arch)
        else:
            raise j.exceptions.RuntimeError('platform not supported')

        j.sal.process.execute(command=j.core.tools.text_replace('rm -rf $GOPATH'), die=True)
        j.core.tools.dir_ensure(self.go_path)

        profile = self.profile_default
        profile.envSet('GOROOT', self.go_root)
        profile.envSet('GOPATH', self.go_path)
        profile.addPath(self.go_root_bin)
        profile.addPath(self.go_path_bin)
        profile.save()

        self.tools.file_download(
            download_url, self.go_path, overwrite=False, retry=3,
            timeout=0, expand=True, removeTopDir=True)

        j.core.tools.dir_ensure("%s/src" % self.go_path)
        j.core.tools.dir_ensure("%s/pkg" % self.go_path)
        j.core.tools.dir_ensure("%s/bin" % self.go_path)

        self.get("github.com/tools/godep")
        self._done_set("install")

    def goraml(self, reset=False):
        """Install (using go get) goraml.

        :param reset: reset installation, defaults to False
        :param reset: bool, optional
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
        """Install (using go get) go-bindata.

        :param reset: reset installation, defaults to False
        :param reset: bool, optional
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
        """install glide"""
        if self._done_get('glide'):
            return
        self.tools.file_download(
            'https://glide.sh/get', '{DIR_TEMP}/installglide.sh', minsizekb=4)
        j.sal.process.execute('. {DIR_TEMP}/installglide.sh', profile=True)
        self._done_set('glide')

    def clean_src_path(self):
        srcpath = self.tools.joinpaths(self.go_path, 'src')
        self.tools.dir_remove(srcpath)

    def get(self, url, install=True, update=True, die=True):
        """
        @param url ,, str url to run the go get command on.
        @param install ,, bool will default build and install the repo if false will only get the repo.
        @param update ,, bool will if True will update requirements if they exist.
        e.g. url=github.com/tools/godep
        """
        download_flag = ''
        update_flag = ''
        if not install:
            download_flag = '-d'
        if update:
            update_flag = '-u'
        j.sal.process.execute('go get %s -v %s %s' % (download_flag, update_flag, url), die=die)

    def package_path_get(self, name, host='github.com', go_path=None):
        """A helper method to get a package path installed by `get`
        Will use this builder's default go path if go_path is not provided

        :param name: pacakge name e.g. containous/go-bindata
        :param host: host, defaults to github.com
        :param go_path: GOPATH, defaults to None
        :type name: str
        """
        if not go_path:
            go_path = self.go_path
        return j.sal.fs.joinPaths(go_path, 'src', host, name)

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
