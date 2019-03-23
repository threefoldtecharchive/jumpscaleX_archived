from Jumpscale import j


class BuilderCoreDns(j.builder.system._BaseClass):
    NAME = "coredns"

    def _init(self):
        self.golang = self.b.runtimes.golang
        self.package_path = j.builder.runtimes.golang.package_path_get('coredns', host='github.com/coredns')

    def build(self, reset=False):
        """

        kosmos 'j.builder.network.coredns.build(reset=False)'

        installs and runs coredns server with redis plugin
        """
        self._init()
        if self._done_check("build", reset):
            return
        # install golang
        j.builder.runtimes.golang.install(reset=False)
        j.builder.runtimes.golang.get('github.com/coredns/coredns', install=False, update=True)

        # go to package path and build (for coredns)
        C="""
        cd {GITDIR}
        git remote add threefoldtech_coredns https://github.com/threefoldtech/coredns
        git fetch threefoldtech_coredns
        git checkout threefoldtech_coredns/master
        make
        
        cp /sandbox/go_proj/src/github.com/coredns/coredns/coredns /sandbox/bin/coredns
        """
        self.tools.run(C,args={"GITDIR":self.package_path},replace=True)

        self._done_set('build')

    def install(self,reset=False):
        """

        kosmos 'j.builder.network.coredns.install(reset=False)'

        :param reset:
        :return:
        """
        self.build(reset=reset)

    def sandbox(self,  dest_path="/tmp/builders/coredns", sandbox_dir="sandbox", reset=False, create_flist=False, zhub_instance=None):
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

        if self._done_check('sandbox',reset):
            return
        self.build(reset=reset)

        coredns_bin = j.sal.fs.joinPaths(self.package_path, 'coredns')
        dir_dest = j.sal.fs.joinPaths(dest_path, coredns_bin[1:]) 
        j.builder.tools.dir_ensure(dir_dest)
        j.sal.fs.copyFile(coredns_bin, dir_dest)

        dir_dest = j.sal.fs.joinPaths(dest_path, sandbox_dir, 'etc/ssl/certs/')
        j.builder.tools.dir_ensure(dir_dest)
        j.sal.fs.copyDirTree('/etc/ssl/certs', dir_dest)

        startup_file = j.sal.fs.joinPaths(j.sal.fs.getDirName(__file__), 'templates', 'coredns_startup.toml')
        self.startup = j.sal.fs.readFile(startup_file)
        j.sal.fs.copyFile(startup_file,  j.sal.fs.joinPaths(dest_path, sandbox_dir))

        self._done_set('sandbox')

        if create_flist:
            self.flist_create(dest_path, zhub_instance)

    def start(self, config_file=None, args=None):
        """Starts coredns with the configuration file provided

        :param config_file: config file path e.g. ~/coredns.json
        :raises j.exceptions.RuntimeError: in case config file does not exist
        :return: tmux pane
        :rtype: tmux.Pane
        """
        self._init()
        cmd = "{coredns_path}/coredns -conf {path_config}".format(coredns_path=self.package_path, path_config=config_file)
        return j.tools.tmux.execute(window="coredns", cmd=cmd)


    def test(self):

        if not j.sal.process.checkInstalled(j.builder.network.coredns.NAME):
            # j.builder.network.coredns.stop()
            # j.builder.network.coredns.build(reset=True)
            j.builder.network.coredns.sandbox(reset=True)

        # try to start/stop
        tmux_pane = j.builder.network.coredns.start()
        tmux_process = tmux_pane.process_obj
        child_process = tmux_pane.process_obj_child
        assert child_process.is_running()

        #CONFIGURE REDIS BACKEND
        #TODO: need to do a test on UDP port for some DNS queries

