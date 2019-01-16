from Jumpscale import j

BaseClass = j.application.JSBaseClass


class BuilderBaseClass(BaseClass):
    Name = "base"

    def __init__(self):
        BaseClass.__init__(self,True)
        self.bins = []
        self.dirs = []
        self._init()

    @property
    def system(self):
        return j.builder.system

    @property
    def tools(self):
        return j.builder.tools

    @property
    def b(self):
        return j.builder

    def sandbox_create(self, dest):
        """
        Creates a sandbox from the built files by collecting the bins and the libs then collecting any files used from
        the builder
        :param dest: the destination of the created sandbox 
        """
        # first we ensure the destination directory exists
        if not dest.endswith("sandbox"):
            dest = j.sal.fs.joinPaths(dest, "sandbox")
        j.builder.tools.dir_ensure(dest)
        lib_dest = j.sal.fs.joinPaths(dest, "lib")
        j.builder.tools.dir_ensure(lib_dest)
        for bin in self.bins:
            j.tools.sandboxer.libs_sandbox(bin, lib_dest)

        bin_dest = j.sal.fs.joinPaths(dest, "bin")
        j.builder.tools.dir_ensure(bin_dest)
        for bin in self.bins:
            j.sal.fs.copyFile(bin, j.sal.fs.joinPaths(bin_dest, j.sal.fs.getBaseName(bin)))

        for dir in self.dirs:
            if dir.startswith('/'):
                dir = dir[1:]
            dir_dest = j.sal.fs.joinPaths(dest, dir)
            j.builder.tools.dir_ensure(dir_dest)
            j.sal.fs.copyDirTree(dir, j.sal.fs.joinPaths(dest, dir))

    def flist_create(self, hub_instance=None):
        """
        build a flist for the builder and upload the created flist to the hub

        This method builds and optionally upload the flist to the hub

        :param hub_instance: instance name of the zerohub client to use to upload the flist, defaults to None if None
        the flist will be created but not uploaded to the hub
        :param hub_instance: str, optional
        :raises j.exceptions.Input: raised if the zerohub client instance does not exist in the config manager
        :return: path to the tar.gz created
        :rtype: str
        """
        sandbox_dir = "/tmp/builders/{}".format(self.NAME)
        self.sandbox_create(sandbox_dir)

        self._logger.info('building flist')
        build_dir = j.sal.fs.getTmpDirPath()
        tarfile = '/tmp/{}.tar.gz'.format(self.Name)

        j.sal.process.execute('tar czf {} -C {} .'.format(tarfile, sandbox_dir))

        if hub_instance:
            if not j.clients.zerohub.exists(hub_instance):
                raise j.exceptions.Input("hub instance %s does not exists, can't upload to the hub" % hub_instance)
            hub = j.clients.zerohub.get(hub_instance)
            hub.authentificate()
            self._logger.info("uploading flist to the hub")
            hub.upload(tarfile)
            self._logger.info("uploaded at https://hub.gig.tech/%s/etcd-3.3.4.flist", hub.config.data['username'])

        return tarfile
