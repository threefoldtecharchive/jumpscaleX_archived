from Jumpscale import j
builder_method = j.builder.system.builder_method


class BuilderZdb(j.builder.system._BaseClass):
    NAME = '0-db'

    def _init(self):
        self.git_url = 'https://github.com/threefoldtech/0-db.git'
        self.DIR_BUILD = self._replace("{DIR_TEMP}/zdb")

    @builder_method()
    def build(self):
        """
        build zdb
        :return:
        """
        self.tools.dir_ensure(self.DIR_BUILD)
        C = """
        cd {DIR_BUILD}
        git clone https://github.com/threefoldtech/0-db.git --branch development
        cd {DIR_BUILD}/0-db
        make
        """
        self._execute(C)

    @builder_method()
    def install(self):
        """
        Installs the zdb binary to the correct location
        """
        zdb_bin_path = j.builder.tools.joinpaths(self.DIR_BUILD, '0-db/bin/zdb')
        self._copy(zdb_bin_path, '{DIR_BIN}')

    @property
    def startup_cmds(self):
        addr = '127.0.0.1'
        port = 9900
        datadir = self.DIR_BUILD
        mode = 'seq'
        adminsecret = '123456'
        idir = '{}/index/'.format(datadir)
        ddir = '{}/data/'.format(datadir)
        j.sal.fs.createDir(idir)
        j.sal.fs.createDir(ddir)
        cmd = '/sandbox/bin/zdb --listen {} --port {} --index {} --data {} --mode {} --admin {} --protect'.format(
            addr, port, idir, ddir, mode, adminsecret)
        cmds = [j.tools.startupcmd.get(name=self.NAME, cmd=cmd)]
        return cmds

    @builder_method()
    def sandbox(self):
        bin_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox")
        self.tools.dir_ensure(bin_dest)
        zdb_bin_path = self.tools.joinpaths("{DIR_BIN}", 'zdb')
        self._copy(zdb_bin_path, bin_dest)

    @builder_method()
    def clean(self):
        self._remove(self.DIR_BUILD)
        self._remove(self.DIR_SANDBOX)

    @builder_method()
    def test(self):
        if self.running():
            self.stop()

        self.start()
        admin_client = j.clients.zdb.client_admin_get()
        namespaces = admin_client.namespaces_list()
        assert namespaces == ['default']

        admin_client.namespace_new(name='test', maxsize=10)
        namespaces = admin_client.namespaces_list()
        assert namespaces == ['default', 'test']

        admin_client.namespace_delete('test')
        self.stop()

        print('TEST OK')
