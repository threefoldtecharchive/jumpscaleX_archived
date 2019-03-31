from Jumpscale import j

builder_method = j.builder.system.builder_method

class BuilderGolang(j.builder.system._BaseClass):

    NAME = 'go'
    STABLE_VERSION = '1.12'
    DOWNLOAD_URL = 'https://dl.google.com/go/go{version}.{platform}-{arch}.tar.gz'


    def _init(self):
        self.base_dir = j.core.tools.text_replace('{DIR_BASE}')

        self.env = self.bash.profile

        self.DIR_GO_ROOT = self.tools.joinpaths(self.base_dir, 'go')
        self.DIR_GO_PATH = self.tools.joinpaths(self.base_dir, 'go_proj')
        self.DIR_GO_ROOT_BIN = self.tools.joinpaths(self.DIR_GO_ROOT, 'bin')
        self.DIR_GO_PATH_BIN = self.tools.joinpaths(self.DIR_GO_PATH, 'bin')

        self.bash.profile.env_set('GOROOT',self.DIR_GO_ROOT)
        self.bash.profile.env_set('GOPATH',self.DIR_GO_PATH)

        if self.bash.profile.env_exists('GOROOT'):
            go_root = self.bash.profile.env_get('GOROOT')
            self.bash.profile.path_delete(go_root)
        if self.bash.profile.env_exists('GOPATH'):
            go_path = self.bash.profile.env_get('GOPATH')
            self.bash.profile.path_delete(go_path)

        self.bash.profile .save()


    @property
    def version(self):
        """get the current installed go version

        :raises j.exceptions.RuntimeError: in case go is not installed
        :return: go version e.g. 1.11.4
        :rtype: str
        """
        rc, out, err = self._execute('go version', die=False, showout=False)
        if rc:
            raise j.exceptions.RuntimeError('go is not instlled\n%s' % err)
        return j.data.regex.findOne(r'go\d+.\d+.\d+', out)[2:]

    @property
    def is_installed(self):
        """check if go is installed with the latest stable version

        :return: installed and the version is `VERSION_STABLE` or not
        :rtype: bool
        """
        try:
            version = self.version
            return self.STABLE_VERSION in version
        except j.exceptions.RuntimeError:
            return False

    @property
    def current_arch(self):
        """get the current arch string commonly used by go projects

        :return: arch (386 or amd64)
        :rtype: str
        """
        if j.core.platformtype.myplatform.is32bit:
            return  '386'
        return 'amd64'

    @builder_method()
    def install(self):
        """install goq

        kosmos 'j.builder.runtimes.golang.install(reset=True)'

        """
        # only check for linux for now
        if j.core.platformtype.myplatform.isLinux:
            download_url = self.DOWNLOAD_URL.format(version=self.STABLE_VERSION, platform='linux', arch=self.current_arch)
        elif j.core.platformtype.myplatform.isMac:
            download_url = self.DOWNLOAD_URL.format(version=self.STABLE_VERSION, platform='darwin', arch=self.current_arch)
        else:
            raise j.exceptions.RuntimeError('platform not supported')

        self._execute('rm -rf $GOPATH', die=True)
        j.core.tools.dir_ensure(self.DIR_GO_PATH)

        self.env.env_set('GOROOT', self.DIR_GO_ROOT)
        self.env.env_set('GOPATH', self.DIR_GO_PATH)
        self.env.path_add(self.DIR_GO_ROOT_BIN)
        self.env.path_add(self.DIR_GO_PATH_BIN)
        self.env.save()

        self.tools.file_download(
            download_url, self.DIR_GO_ROOT, overwrite=False, retry=3,
            timeout=0, expand=True, removeTopDir=True)

        j.shell()

        if self.tools.file_exists('{DIR_BIN}/go'):
            self._execute('unlink {DIR_BIN}/go')

        self._execute('ln -s $GOROOT/bin/go {DIR_BIN}/go')

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
        self._execute(C)
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
        self._execute(C)
        self._done_set('bindata')

    def glide(self):
        """install glide"""
        if self._done_get('glide'):
            return
        self.tools.file_download(
            'https://glide.sh/get', '{DIR_TEMP}/installglide.sh', minsizekb=4)
        self._execute('. {DIR_TEMP}/installglide.sh')
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
        self._execute('go get %s -v %s %s' % (download_flag, update_flag, url), die=die)

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
            go_path = self.DIR_GO_PATH
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
            dest='%s/src/%s' % (self.DIR_GO_PATH, url),
            ssh=False)
        self._execute('cd %s && godep restore' % dest)

    def _test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key='test_main')
