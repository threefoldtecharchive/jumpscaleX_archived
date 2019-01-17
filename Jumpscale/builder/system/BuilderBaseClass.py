from Jumpscale import j

BaseClass = j.application.JSBaseClass


class BuilderBaseClass(BaseClass):
    def __init__(self):
        BaseClass.__init__(self, True)
        self.bins = []  # list of binaries to copy to the sandbox
        self.dirs = {}  # dict of files/dirs to copy to the sandbox. key is the source and value is the dest in the sandbox
        self.new_dirs = []  # list of dirs to create in the sandbox
        self.new_files = {}  # dict of new files to create. key is the location in the sandbox and the value is the content
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
        :type dest: str
        """
        # first we ensure the destination directory exists
        if not dest.endswith('sandbox'):
            dest = j.sal.fs.joinPaths(dest, 'sandbox')
        j.builder.tools.dir_ensure(dest)

        # copy binaries and lib dependencies
        lib_dest = j.sal.fs.joinPaths(dest, 'lib')
        j.builder.tools.dir_ensure(lib_dest)
        for bin in self.bins:
            j.tools.sandboxer.libs_sandbox(bin, lib_dest)

        bin_dest = j.sal.fs.joinPaths(dest, 'bin')
        j.builder.tools.dir_ensure(bin_dest)
        for bin in self.bins:
            j.sal.fs.copyFile(bin, j.sal.fs.joinPaths(bin_dest, j.sal.fs.getBaseName(bin)))

        # copy dirs in self.dirs
        for src, dir_dest in self.dirs.items():
            file = True if j.sal.fs.getBaseName(src) else False

            # remove the first slash to make sure the path will join correctly
            dir_dest = dir_dest[1:] if dir_dest.startswith('/') else dir_dest
            dir_dest = j.sal.fs.joinPaths(dest, dir_dest)
            j.builder.tools.dir_ensure(dir_dest)

            if file:
                j.sal.fs.copyFile(src, dir_dest)
            else:
                j.sal.fs.copyDirTree(src, dir_dest)

        # create dirs in self.new_dirs
        for dir_dest in self.new_dirs:
            dir_dest = dir_dest[1:] if dir_dest.startswith('/') else dir_dest
            dir_dest = j.sal.fs.joinPaths(dest, dir_dest)
            j.builder.tools.dir_ensure(dir_dest)

        # create files in self.new_files
        for file_dest, content in self.new_files.items():
            file_dest = file_dest[1:] if file_dest.startswith('/') else file_dest
            file_dest = j.sal.fs.joinPaths(dest, file_dest)
            j.builder.tools.file_ensure(file_dest)
            j.builder.tools.file_write(file_dest, content)

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
        tarfile = '/tmp/{}.tar.gz'.format(self.NAME)

        j.sal.process.execute('tar czf {} -C {} .'.format(tarfile, sandbox_dir))

        if hub_instance:
            if not j.clients.zhub._exists(name=hub_instance):
                raise j.exceptions.Input("hub instance %s does not exists, can't upload to the hub" % hub_instance)
            hub = j.clients.zhub.get(hub_instance)
            hub.authenticate()
            self._logger.info("uploading flist to the hub")
            hub.upload(tarfile)
            self._logger.info("uploaded at https://hub.grid.tf/{}/{}.flist".format(hub.username,
                                                                                   self.NAME))

        return tarfile
