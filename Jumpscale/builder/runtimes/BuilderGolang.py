from Jumpscale import j


class BuilderGolang(j.builder.system._BaseClass):

    NAME = 'go'
    STABLE_VERSION = '1.11'
    DOWNLOAD_URL = 'https://dl.google.com/go/go{version}.{platform}-{arch}.tar.gz'

    def reset(self):
        if self.profile_default.envExists('GOROOT'):
            go_root = self.profile_default.envGet('GOROOT')
            self.profile_default.pathDelete(go_root)
            self.profile_js.pathDelete(go_root)
        if self.profile_default.envExists('GOPATH'):
            go_path = self.profile_default.envGet('GOPATH')
            self.profile_default.pathDelete(go_path)

        if self.env.envExists('GOROOT'):
            go_root = self.env.envGet('GOROOT')
            self.env.pathDelete(go_root)
        if self.env.envExists('GOPATH'):
            go_path = self.env.envGet('GOPATH')
            self.env.pathDelete(go_path)

        self.profile_default.deleteAll('GOROOT')
        self.profile_js.deleteAll('GOROOT')
        self.profile_default.deleteAll('GOPATH')
        self.profile_js.deleteAll('GOPATH')
        self.env.deleteAll('GOROOT')
        self.env.deleteAll('GOPATH')

        # ALWAYS SAVE THE DEFAULT FIRST !!!
        self.profile_default.save()
        self.profile_js.save()
        self.env.save()

    def _init(self):
        self.base_dir = j.core.tools.text_replace('{DIR_BASE}')

        self.bash = j.tools.bash.get()
        self.profile_default = self.bash.profileDefault
        self.profile_js = self.bash.profileJS
        self.env = self.bash.profileGet(self.tools.joinpaths(self.base_dir, 'env.sh'))

        self.go_root = self.tools.joinpaths(self.base_dir, 'go')
        self.go_path = self.tools.joinpaths(self.base_dir, 'go_proj')
        self.go_root_bin = self.tools.joinpaths(self.go_root, 'bin')
        self.go_path_bin = self.tools.joinpaths(self.go_path, 'bin')

    def execute(self, command, **kwargs):
        """execute a command with the default profile sourced
           with GOROOT and GOPATH

        :param command: command
        :type command: str
        :return: execution result (return code, output, error)
        :rtype: tuple
        """
        profile_source = 'source %s\n' % self.env.pathProfile
        command = j.core.tools.text_replace(profile_source + command)
        return j.sal.process.execute(command, **kwargs)

    @property
    def version(self):
        """get the current installed go version

        :raises j.exceptions.RuntimeError: in case go is not installed
        :return: go version e.g. 1.11.4
        :rtype: str
        """
        rc, out, err = self.execute('go version', die=False, showout=False)
        if rc:
            raise j.exceptions.RuntimeError('go is not instlled\n%s' % err)
        return j.data.regex.findOne(r'go\d+.\d+.\d+', out)[2:]

    @property
    def is_installed(self):
        """check if go is installed with the latest stable version

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
        """install go

        :param reset: reset installation, defaults to False
        :type reset: bool, optional
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

        self.execute('rm -rf $GOPATH', die=True)
        j.core.tools.dir_ensure(self.go_path)

        self.env.envSet('GOROOT', self.go_root)
        self.env.envSet('GOPATH', self.go_path)
        self.env.addPath(self.go_root_bin)
        self.env.addPath(self.go_path_bin)
        self.env.save()

        self.tools.file_download(
            download_url, self.go_root, overwrite=False, retry=3,
            timeout=0, expand=True, removeTopDir=True)

        if self.tools.file_exists('{DIR_BIN}/go'):
            self.execute('unlink {DIR_BIN}/go')
        self.execute('ln -s $GOROOT/bin/go {DIR_BIN}/go')

        self.get("github.com/tools/godep")
        self._done_set("install")

    def goraml(self, reset=False):
        """install (using go get) goraml.

        :param reset: reset installation, defaults to False
        :type reset: bool, optional
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
        self.execute(C)
        self._done_set('goraml')

    def bindata(self, reset=False):
        """install (using go get) go-bindata.

        :param reset: reset installation, defaults to False
        :type reset: bool, optional
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
        self.execute(C)
        self._done_set('bindata')

    def glide(self):
        """install glide"""
        if self._done_get('glide'):
            return
        self.tools.file_download(
            'https://glide.sh/get', '{DIR_TEMP}/installglide.sh', minsizekb=4)
        self.execute('. {DIR_TEMP}/installglide.sh')
        self._done_set('glide')

    def get(self, url, install=True, update=True, die=True):
        """go get a package

        :param url: pacakge url e.g. github.com/tools/godep
        :type url:  str
        :param install: build and install the repo if false will only get the repo, defaults to True
        :type install: bool, optional
        :param update: will update requirements if they exist, defaults to True
        :type update: bool, optional
        :param die: raise a RuntimeError if failed, defaults to True
        :type die: bool, optional
        """
        download_flag = ''
        update_flag = ''
        if not install:
            download_flag = '-d'
        if update:
            update_flag = '-u'
        self.execute('go get %s -v %s %s' % (download_flag, update_flag, url), die=die)

    def package_path_get(self, name, host='github.com', go_path=None):
        """A helper method to get a package path installed by `get`
        Will use this builder's default go path if go_path is not provided

        :param name: pacakge name e.g. containous/go-bindata
        :type name: str
        :param host: host, defaults to github.com
        :type host: str
        :param go_path: GOPATH, defaults to None
        :type go_path: str

        :return: go package path
        :rtype: str
        """
        if not go_path:
            go_path = self.go_path
        return self.tools.joinpaths(go_path, 'src', host, name)

    def godep(self, url, branch=None, depth=1):
        """install a package using godep

        :param url: package url e.g. github.com/tools/godep
        :type url: str
        :param branch: a specific branch, defaults to None
        :type branch: str, optional
        :param depth: depth to pull with, defaults to 1
        :type depth: int, optional
        """

        self.clean_src_path()
        pullurl = "git@%s.git" % url.replace('/', ':', 1)

        dest = j.clients.git.pullGitRepo(
            pullurl,
            branch=branch,
            depth=depth,
            dest='%s/src/%s' % (self.go_path, url),
            ssh=False)
        self.execute('cd %s && godep restore' % dest)

    def _test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key='test_main')
