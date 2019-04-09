from Jumpscale import j
import os
import textwrap
builder_method = j.builder.system.builder_method



class BuilderMinio(j.builder.system._BaseClass):
    NAME = "minio"

    def _init(self):
        self.DIR_BUILD = j.builder.runtimes.golang.package_path_get('minio', host='github.com/minio')
        self.datadir = ''

    @builder_method()
    def build(self):
        """
        Builds minio
        """
        self.profile_sandbox_select()
        self.tools.dir_ensure(self.DIR_BUILD)
        j.builder.runtimes.golang.install()
        j.builder.runtimes.golang.get('github.com/minio/minio', install=False, update=True)
        self._execute('cd {DIR_BUILD}; make')

    @builder_method()
    def install(self):
        """
        Installs minio
        """
        self._copy('{DIR_BUILD}/minio', '{DIR_BIN}')

    @property
    def startup_cmds(self):
        """
        Starts minio.
        """
        self.datadir = self.DIR_BUILD
        address = '0.0.0.0'
        self.tools.dir_ensure(self.datadir)
        port = 9000
        access_key = 'admin'
        secret_key = 'adminadmin'
        cmd = "MINIO_ACCESS_KEY={} MINIO_SECRET_KEY={} minio server --address {}:{} {}".format(access_key, secret_key, address, port, self.datadir)
        cmds = [j.tools.startupcmd.get(name=self.NAME, cmd=cmd)]
        return cmds

    @builder_method()
    def clean(self):
        self._remove(self.DIR_BUILD)
        self._remove(self.DIR_SANDBOX)
    
    @builder_method()
    def sandbox(self):
        bin_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, "sandbox")
        self.tools.dir_ensure(bin_dest)
        bin_path = self.tools.joinpaths("{DIR_BIN}", self.NAME)
        self._copy(bin_path, bin_dest)

    @builder_method()
    def test(self):
        if self.running():
            self.stop()

        self.start()
        pid = j.sal.process.getProcessPid(self.NAME)
        assert pid is not []
        self.stop()

        print('TEST OK')

    @builder_method()
    def uninstall(self):
        bin_path = self.tools.joinpaths("{DIR_BIN}", self.NAME)
        self._remove(bin_path)
        self.clean()
