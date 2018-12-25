from Jumpscale import j
from time import sleep




class BuilderTIDB(j.builder.system._BaseClass):
    """
    Installs TIDB.
    """
    NAME = 'tidb-server'

    def _init(self):
        self.BUILDDIR = j.core.tools.text_replace("{DIR_VAR}/build/tidb/")

    def build(self, install=True, reset=False):
        if self._done_check("build", reset):
            return
        j.core.tools.dir_ensure(self.BUILDDIR)
        tidb_url = 'http://download.pingcap.org/tidb-latest-linux-amd64.tar.gz'
        j.builder.tools.file_download(
            tidb_url, overwrite=False, to=self.BUILDDIR, expand=True, removeTopDir=True)
        self._done_set('build')

        if install:
            self.install(False)

    def install(self, start=True, reset=False):
        """
        install, move files to appropriate places, and create relavent configs
        """
        if self._done_check("install", reset):
            return
        j.sal.process.execute("cp {DIR_VAR}/build/tidb/bin/* {DIR_BIN}/")
        self._done_set('install')

        if start:
            self.start()

    def start_pd_server(self):
        data_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, 'pd')
        pm = j.builder.system.processmanager.get()
        pm.ensure(
            'pd-server',
            'pd-server --data-dir={data_dir}'.format(data_dir=data_dir)
        )

    def start_tikv(self):
        store_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, 'tikv')
        pm = j.builder.system.processmanager.get()
        pm.ensure(
            "tikv-server",
            "tikv-server --pd='127.0.0.1:2379' --store={store_dir}".format(
                store_dir=store_dir)
        )

    def start_tidb(self):
        pm = j.builder.system.processmanager.get()
        pm.ensure(
            "tidb-server",
            "tidb-server --path='127.0.0.1:2379' --store=TiKV"
        )

    def start(self):
        """
        Read docs here.
        https://github.com/pingcap/docs/blob/master/op-guide/clustering.md
        """
        # Start a standalone cluster
        self.start_pd_server()
        if not self._check_running('pd-server', timeout=30):
            raise j.exceptions.RuntimeError("tipd didn't start")

        self.start_tikv()
        if not self._check_running('tikv-server', timeout=30):
            raise j.exceptions.RuntimeError("tikv didn't start")

        self.start_tidb()
        if not self._check_running('tidb-server', timeout=30):
            raise j.exceptions.RuntimeError("tidb didn't start")

    def stop(self):
        pm = j.builder.system.processmanager.get()
        pm.stop("tidb-server")
        pm.stop("pd-server")
        pm.stop("tikv-server")

    def _check_running(self, name, timeout=30):
        """
        check that a process is running.
        name: str, name of the process to check
        timout: int, timeout in second
        """
        now = j.data.time.epoch
        cmd = "ps aux | grep {}".format(name)
        rc, _, _ = j.sal.process.execute(cmd, die=False, showout=False)
        while rc != 0 and j.data.time.epoch < (now + timeout):
            rc, _, _ = j.sal.process.execute(cmd, die=False, showout=False)
            if rc != 0:
                sleep(2)
        return rc == 0
