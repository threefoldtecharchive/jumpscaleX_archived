from Jumpscale import j

builder_method = j.builder.system._builder_method

class BuilderCoreDns(j.builder.system._BaseClass):
    NAME = "coredns"

    @builder_method(log=False,done_check=True)
    def _init(self):
        self.golang = j.builder.runtimes.golang
        self._package_path = j.builder.runtimes.golang.package_path_get('coredns', host='github.com/coredns')

    @builder_method()
    def build(self):
        """

        kosmos 'j.builder.network.coredns.build(reset=False)'

        installs and runs coredns server with redis plugin
        """
        print(1)
        return(2)
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
        self.tools.run(C,args={"GITDIR":self._package_path},replace=True)


    @builder_method()
    def sandbox(self, zhub_client=None):

        coredns_bin = j.sal.fs.joinPaths(self._package_path, 'coredns')
        dir_dest = j.sal.fs.joinPaths(dest_path, coredns_bin[1:]) 
        j.builder.tools.dir_ensure(dir_dest)
        j.sal.fs.copyFile(coredns_bin, dir_dest)

        dir_dest = j.sal.fs.joinPaths(dest_path, self._sandbox_dir, 'etc/ssl/certs/')
        j.builder.tools.dir_ensure(dir_dest)
        j.sal.fs.copyDirTree('/etc/ssl/certs', dir_dest)

        startup_file = j.sal.fs.joinPaths(j.sal.fs.getDirName(__file__), 'templates', 'coredns_startup.toml')
        self.startup = j.sal.fs.readFile(startup_file)
        j.sal.fs.copyFile(startup_file,  j.sal.fs.joinPaths(dest_path, self._sandbox_dir))


    @property
    def startup_cmds(self):
        cmd = "{coredns_path}/coredns -conf {path_config}".format(coredns_path=self._package_path, path_config=config_file)
        cmds = [j.data.startupcmd.get(cmd)
        return cmds

    # @builder_method()
    # def start(self, config_file=None, args=None):
    #     """Starts coredns with the configuration file provided
    #
    #     :param config_file: config file path e.g. ~/coredns.json
    #     :raises j.exceptions.RuntimeError: in case config file does not exist
    #     :return: tmux pane
    #     :rtype: tmux.Pane
    #     """
    #     self._init()

    #     return j.tools.tmux.execute(window="coredns", cmd=cmd)


    @builder_method()
    def test(self,reset=False):
        """
        build on local ubuntu & test a client
        :return:
        """



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

        #use the test on the client


    def test_zos(self,zosclient=None,flist=None,build=False):

        if build:
            #TODO:*1 build the app and sandbox & create flist, created flist is then used here in this test
            pass

        if not flist:
            flist = 1 #TODO:*1 get the std flist which is on tfhub

        if not zosclient:
            zosclient = j.clients.zos.get("test") #NEEDS TO EXIST

        #launch container on selected zosclient




