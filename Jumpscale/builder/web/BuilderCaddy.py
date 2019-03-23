from Jumpscale import j


class BuilderCaddy(j.builder.system._BaseClass):
    NAME = "caddy"

    def _init(self):
        self.go_runtime = j.builder.runtimes.golang
        

    def reset(self):
        self.stop()
        self._init()
        j.builder.tools.dir_remove("{DIR_BIN}/caddy")

    def build(self, reset=False, plugins=None):
        """
        Get/Build the binaries of caddy itself.

        :param reset: reset the build process, defaults to False
        :type reset: bool, optional
        :param plugins: list of plugins names to be installed, defaults to None
        :type plugins: list, optional
        :raises j.exceptions.RuntimeError: if platform is not supported
        """
        if not j.core.platformtype.myplatform.isUbuntu:
            raise j.exceptions.RuntimeError("only ubuntu supported")

        if self._done_check('build', reset):
            return

        if not self.go_runtime.is_installed:
            self.go_runtime.install()

        # build caddy from source using our caddyman
        j.clients.git.pullGitRepo("https://github.com/incubaid/caddyman", dest="/tmp/caddyman")
        self.go_runtime.execute("cd /tmp/caddyman && chmod u+x caddyman.sh")
        if not plugins:
            plugins = ["iyo"]
        cmd = "/tmp/caddyman/caddyman.sh install {plugins}".format(plugins=" ".join(plugins))
        self.go_runtime.execute(cmd, timeout=60*60)
        self._done_set('build')

    def install(self, plugins=None, reset=False):
        """
        will build if required & then install binary on right location

        :param plugins: plugins to build with if not build already, defaults to None
        :type plugins: list, optional
        :param reset: reset build and installation, defaults to False
        :type reset: bool, optional
        """
        if not self._done_check('build', reset):
            self.build(plugins=plugins, reset=reset)

        if self._done_check('install', reset):
            return

        caddy_bin_path = self.tools.joinpaths(self.go_runtime.go_path_bin, self.NAME)
        j.builder.tools.file_copy(caddy_bin_path, '{DIR_BIN}/caddy')

        self._done_set('install')

    def start(self, config_file=None, agree=True):
        """start caddy

        :param config_file: config file path (will use ./Caddyfile if not provided), defaults to None
        :type config_file: str, optional
        :param agree: agree to Let's Encrypt Subscriber Agreement, defaults to True
        :type agree: bool, optional
        :raises RuntimeError: if config file doesn't exist
        """
        cmd = j.core.tools.text_replace("{DIR_BIN}/caddy")

        if config_file:
            configpath = j.core.tools.text_replace(config_file)
            if not j.builder.tools.exists(configpath):
                raise RuntimeError('config file does not exist: %s' % configpath)
            cmd += ' -conf=%s' % configpath

        if agree:
            cmd += ' -agree'

        cmd = 'ulimit -n 8192; %s' % cmd
        return j.tools.tmux.execute(cmd, window=self.NAME, pane=self.NAME, reset=True)

    def stop(self, pid=None, sig=None):
        """Stops process

        :param pid: pid of the process, if not given, will kill by name
        :type pid: long, defaults to None
        :param sig: signal, if not given, SIGKILL will be used
        :type sig: int, defaults to None
        """
        if pid:
            j.sal.process.kill(pid, sig)
        else:
            full_path = j.sal.fs.joinPaths(j.core.dirs.BINDIR, self.NAME)
            j.sal.process.killProcessByName(full_path, sig)


    def sandbox(self, dest_path='/tmp/builder/caddy',create_flist=True, zhub_instance=None, reset=False):

        '''Copy built bins to dest_path and create flist if create_flist = True

        :param dest_path: destination path to copy files into
        :type dest_path: str
        :param sandbox_dir: path to sandbox
        :type sandbox_dir: str
        :param reset: reset sandbox file transfer
        :type reset: bool
        :param create_flist: create flist after copying files
        :type create_flist:bool
        :param zhub_instance: hub instance to upload flist to
        :type zhub_instance:str
        '''

        if self._done_check('sandbox') and reset is False:
             return
        self.build(reset = reset)
        bin_dest = j.sal.fs.joinPaths(dest_path, 'sandbox', 'bin')
        self.tools.dir_ensure(bin_dest)
        caddy_bin_path = self.tools.joinpaths(self.go_runtime.go_path_bin, self.NAME)
        self.tools.file_copy(caddy_bin_path, bin_dest)
        if create_flist:
            print(self.flist_create(sandbox_dir=dest_path, hub_instance=zhub_instance))
        self._done_set('sandbox')
    
    def _test(self, name=""):
        """Run tests under tests directory

        :param name: basename of the file to run, defaults to "".
        :type name: str, optional
        """
        self._test_run(name=name, obj_key='test_main')