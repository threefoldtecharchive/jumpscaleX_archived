from Jumpscale import j





class BuilderEtcd(j.builder.system._BaseClass):
    NAME = "etcd"

    def build(self, reset=False):
        """
        Build and start etcd

        @start, bool start etcd after buildinf or not
        @host, string. host of this node in the cluster e.g: http://etcd1.com
        @peer, list of string, list of all node in the cluster. [http://etcd1.com, http://etcd2.com, http://etcd3.com]
        """
        if self.doneCheck("build", reset):
            return

        j.builder.runtimes.golang.install()

        # FYI, REPO_PATH: github.com/coreos/etcd
        _script = """
        set -ex
        ORG_PATH="github.com/coreos"
        REPO_PATH="${ORG_PATH}/etcd"

        go get -x -d -u github.com/coreos/etcd

        cd {DIR_BASE}/go/src/$REPO_PATH

        # first checkout master to prevent error if already in detached mode
        git checkout master

        go get -d .

        CGO_ENABLED=0 go build $GO_BUILD_FLAGS -installsuffix cgo -ldflags "-s -X ${REPO_PATH}/cmd/vendor/${REPO_PATH}/version.GitSHA=${GIT_SHA}" -o {DIR_BIN}/etcd ${REPO_PATH}/cmd/etcd
        CGO_ENABLED=0 go build $GO_BUILD_FLAGS -installsuffix cgo -ldflags "-s" -o {DIR_BIN}/etcdctl ${REPO_PATH}/cmd/etcdctl
        """

        script = j.builder.sandbox.replaceEnvironInText(_script)
        j.sal.process.execute(script, profile=True)
        j.builder.sandbox.addPath("{DIR_BASE}/bin")

        self.doneSet("build")

    def install(self):
        if self.doneCheck("install"):
            return

        url = "https://github.com/coreos/etcd/releases/download/v3.3.4/etcd-v3.3.4-linux-amd64.tar.gz"
        dest = j.sal.fs.getTmpDirPath()
        try:
            expanded = j.builder.core.file_download(url, dest, expand=True, minsizekb=0)
            j.builder.core.file_copy(j.sal.fs.joinPaths(expanded, 'etcd'), j.dirs.BINDIR)
            j.builder.core.file_copy(j.sal.fs.joinPaths(expanded, 'etcdctl'), j.dirs.BINDIR)
        finally:
            j.builder.core.dir_remove(dest)

        self.doneSet("install")

    def build_flist(self, hub_instance=None):
        """
        build a flist for etcd

        This method builds and optionally upload the flist to the hub

        :param hub_instance: instance name of the zerohub client to use to upload the flist, defaults to None
        :param hub_instance: str, optional
        :raises j.exceptions.Input: raised if the zerohub client instance does not exist in the config manager
        :return: path to the tar.gz created
        :rtype: str
        """

        if not self.isInstalled():
            self.install()

        self._logger.info("building flist")
        build_dir = j.sal.fs.getTmpDirPath()
        tarfile = '/tmp/etcd-3.3.4.tar.gz'
        bin_dir = j.sal.fs.joinPaths(build_dir, 'bin')
        j.builder.core.dir_ensure(bin_dir)
        j.builder.core.file_copy(j.sal.fs.joinPaths(j.dirs.BINDIR, 'etcd'), bin_dir)
        j.builder.core.file_copy(j.sal.fs.joinPaths(j.dirs.BINDIR, 'etcdctl'), bin_dir)

        j.sal.process.execute('tar czf {} -C {} .'.format(tarfile, build_dir))

        if hub_instance:
            if not j.clients.zerohub.exists(hub_instance):
                raise j.exceptions.Input("hub instance %s does not exists, can't upload to the hub" % hub_instance)
            hub = j.clients.zerohub.get(hub_instance)
            hub.authentificate()
            self._logger.info("uploading flist to the hub")
            hub.upload(tarfile)
            self._logger.info("uploaded at https://hub.gig.tech/%s/etcd-3.3.4.flist", hub.config.data['username'])

        return tarfile

    def start(self, host=None, peers=None):
        j.builder.system.process.kill("etcd")
        if host and peers:
            cmd = self._etcd_cluster_cmd(host, peers)
        else:
            cmd = '{DIR_BIN}/etcd'
        pm = j.builder.system.processmanager.get()
        pm.ensure("etcd", cmd)

    def _etcd_cluster_cmd(self, host, peers=[]):
        """
        return the command to execute to launch etcd as a static cluster
        @host, string. host of this node in the cluster e.g: http://etcd1.com
        @peer, list of string, list of all node in the cluster. [http://etcd1.com, http://etcd2.com, http://etcd3.com]
        """
        if host not in peers:
            peers.append(host)

        cluster = ""
        number = None
        for i, peer in enumerate(peers):
            cluster += 'infra{i}={host}:2380,'.format(i=i, host=peer)
            if peer == host:
                number = i
        cluster = cluster.rstrip(",")

        host = host.lstrip("http://").lstrip('https://')
        cmd = """{DIR_BIN}/etcd -name infra{i} -initial-advertise-peer-urls http://{host}:2380 \
      -listen-peer-urls http://{host}:2380 \
      -listen-client-urls http://{host}:2379,http://127.0.0.1:2379,http://{host}:4001,http://127.0.0.1:4001 \
      -advertise-client-urls http://{host}:2379,http://{host}:4001 \
      -initial-cluster-token etcd-cluster-1 \
      -initial-cluster {cluster} \
      -initial-cluster-state new \
    """.format(host=host, cluster=cluster, i=number)
        return j.core.tools.text_replace(cmd)
