from Jumpscale import j

builder_method = j.builder.system.builder_method


ALL_PLUGINS = {
    'realip': 'github.com/captncraig/caddy-realip',
    'git': 'github.com/abiosoft/caddy-git',
    'proxyprotocol': 'github.com/mastercactapus/caddy-proxyprotocol',
    'locale': 'github.com/simia-tech/caddy-locale',
    'cache': 'github.com/nicolasazrak/caddy-cache',
    'authz': 'github.com/casbin/caddy-authz',
    'filter': 'github.com/echocat/caddy-filter',
    'minify': 'github.com/hacdias/caddy-minify',
    'ipfilter': 'github.com/pyed/ipfilter',
    'ratelimit': 'github.com/xuqingfeng/caddy-rate-limit',
    'search': 'github.com/pedronasser/caddy-search',
    'expires': 'github.com/epicagency/caddy-expires',
    'cors': 'github.com/captncraig/cors/caddy',
    'nobots': 'github.com/Xumeiquer/nobots',
    'login': 'github.com/tarent/loginsrv/caddy',
    'reauth': 'github.com/freman/caddy-reauth',
    'jwt': 'github.com/BTBurke/caddy-jwt',
    'jsonp': 'github.com/pschlump/caddy-jsonp',
    'upload': 'blitznote.com/src/caddy.upload',
    'multipass': 'github.com/namsral/multipass/caddy',
    'datadog': 'github.com/payintech/caddy-datadog',
    'prometheus': 'github.com/miekg/caddy-prometheus',
    'cgi': 'github.com/jung-kurt/caddy-cgi',
    'filemanager': 'github.com/filebrowser/caddy',
    'iyofilemanager': 'github.com/itsyouonline/filemanager/caddy/filemanager',
    'webdav': 'github.com/hacdias/caddy-webdav',
    'jekyll': 'github.com/hacdias/filemanager/caddy/jekyll',
    'hugo': 'github.com/hacdias/filemanager/caddy/hugo',
    'mailout': 'github.com/SchumacherFM/mailout',
    'awses': 'github.com/miquella/caddy-awses',
    'awslambda': 'github.com/coopernurse/caddy-awslambda',
    'grpc': 'github.com/pieterlouw/caddy-grpc',
    'gopkg': 'github.com/zikes/gopkg',
    'restic': 'github.com/restic/caddy',
    'iyo': 'github.com/itsyouonline/caddy-integration/oauth',
    'dns': 'github.com/coredns/coredns',
    'wsproxy': 'github.com/incubaid/wsproxy',
}


PLUGIN_DIRECTIVES = {
    'iyo': 'oauth',
    'dns': 'dns',
    'wsproxy': 'wsproxy',
}


class BuilderCaddy(j.builder.system._BaseClass):
    NAME = "caddy"
    PLUGINS = ['iyo', 'filemanager']  # PLEASE ADD MORE PLUGINS #TODO:*1

    def _init(self):
        self.go_runtime = j.builder.runtimes.golang
        self.package_path = self.go_runtime.package_path_get('mholt/caddy')
        self.plugins_file = self.tools.joinpaths(self.package_path, 'caddyhttp/httpserver/plugin.go')
        self.main_file = self.tools.joinpaths(self.package_path, 'caddy/caddymain/run.go')

    def clean(self):
        self.stop()
        self._init()
        j.builder.tools.dir_remove("{DIR_BIN}/caddy")

    def _append_after(self, file_path, match, new_line):
        content = self.tools.file_read(file_path)

        lines = content.split('\n')

        line_no = None
        match = match.lower()
        for i, line in enumerate(lines):
            if match in line.lower():
                line_no = i
                break

        if line_no is None:
            raise ValueError('cannot find "%s" in content' % match)

        lines.insert(line_no + 1, new_line)
        self.tools.file_write(file_path, '\n'.join(lines))

    def update_imports_and_directves(self, url, directive=None):
        self._append_after(
            self.main_file, 'This is where other plugins get plugged in (imported)',
            '_ "%s"' % url
        )
        self._execute('gofmt -w %s' % self.main_file)

        if not directive:
            return

        self._append_after(
            self.plugins_file, '"prometheus",', '"%s",' % directive
        )

        self._execute('gofmt -w %s' % self.main_file)

    def get_plugin(self, name):
        """get a supported plugin

        :param name: name
        :type name: str
        :raises j.exceptions.RuntimeError: in case the plugin not supported
        """

        if name not in ALL_PLUGINS:
            raise j.exceptions.RuntimeError('plugin not supported')

        url = ALL_PLUGINS[name]
        self.go_runtime.get(url, install=False)
        self.update_imports_and_directves(url, PLUGIN_DIRECTIVES.get(name))

    @builder_method()
    def build(self, plugins=None):
        """
        Get/Build the binaries of caddy itself.

        :param plugins: list of plugins names to be installed, defaults to None
        :type plugins: list, optional
        :raises j.exceptions.RuntimeError: if platform is not supported
        """
        if not j.core.platformtype.myplatform.isUbuntu:
            raise j.exceptions.RuntimeError("only ubuntu supported")

        # install go runtime
        self.go_runtime.install()

        # get caddy and plugins source
        self.go_runtime.get("github.com/mholt/caddy/caddy")
        if not plugins:
            plugins = self.PLUGINS

        for plugin in plugins:
            self.get_plugin(plugin)

        # build caddy
        self.go_runtime.get("github.com/caddyserver/builds")
        self._execute("cd $GOPATH/src/github.com/mholt/caddy/caddy;go run build.go && cp caddy $GOPATH/bin")

    @builder_method()
    def install(self, plugins=None):
        """
        will build if required & then install binary on right location

        :param plugins: plugins to build with if not build already, defaults to None

        kosmos 'j.builder.web.caddy.install()'

        """

        caddy_bin_path = self.tools.joinpaths(
            self.go_runtime.DIR_GO_PATH_BIN, self.NAME
        )
        j.builder.tools.file_copy(caddy_bin_path, "{DIR_BIN}/caddy")

    @property
    def startup_cmds(self):
        cmd = j.tools.startupcmd.get('caddy', 'caddy', path='/sandbox/bin')
        return [cmd]

    @builder_method()
    def sandbox(self, reset=False, zhub_client=None, flist_create=False):
        bin_dest = j.sal.fs.joinPaths("/sandbox/var/build", "{}/sandbox".format(self.DIR_SANDBOX))
        self.tools.dir_ensure(bin_dest)
        caddy_bin_path = self.tools.joinpaths(
            "{go_path}/src/github.com/mholt/caddy/caddy".format(go_path=self.go_runtime.DIR_GO_PATH), self.NAME)
        self.tools.file_copy(caddy_bin_path, bin_dest)

    def _test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key="test_main")
