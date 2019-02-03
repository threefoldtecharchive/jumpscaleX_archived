from Jumpscale import j

BaseClass = j.application.JSBaseClass


class BuilderBaseClass(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        self.bins = []  # list of binaries to copy to sandbox/bin/ in the flist
        self.dirs = {}  # dict of files/dirs to copy to the sandbox/ in the flist. key is the source and value is the dest under sandbox/
        self.new_dirs = []  # list of dirs to create under sandbox/ in the flist
        self.new_files = {}  # dict of new files to create in the flist. key is the location under sandbox/ and the value is the content
        self.startup = ''  # content of the startup script, placed at the root of the flist
        self.root_files = {}
        self.root_dirs = {}  # dict of paths to be copied as is. key is the location, and value is the dest (without sandbox)
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
        sandbox_dest = j.sal.fs.joinPaths(dest, 'sandbox')
        j.builder.tools.dir_ensure(sandbox_dest)

        # copy binaries and lib dependencies
        lib_dest = j.sal.fs.joinPaths(sandbox_dest, 'lib')
        j.builder.tools.dir_ensure(lib_dest)
        for bin in self.bins:
            j.tools.sandboxer.libs_sandbox(bin, lib_dest, exclude_sys_libs=False)

        bin_dest = j.sal.fs.joinPaths(sandbox_dest, 'bin')
        j.builder.tools.dir_ensure(bin_dest)
        for bin in self.bins:
            j.sal.fs.copyFile(bin, j.sal.fs.joinPaths(bin_dest, j.sal.fs.getBaseName(bin)))

        # create dirs in self.new_dirs
        for dir_dest in self.new_dirs:
            dir_dest = j.sal.fs.joinPaths(sandbox_dest, self.tools.path_relative(dir_dest))
            j.builder.tools.dir_ensure(dir_dest)

        self.copy_dirs(self.dirs, sandbox_dest)
        self.write_files(self.new_files, sandbox_dest)

    def copy_dirs(self, dirs, dest):
        """Copy dirs or files

        :param dirs: a dict where the key is the source and the value is the destination
        :type dirs: dict
        :param dest: the root path to be appended to the paths in dirs
        :type dest: str
        """
        for src, to in dirs.items():
            file = True if j.sal.fs.isFile(src) else False
            dir_dest = j.sal.fs.joinPaths(dest, self.tools.path_relative(to))
            j.builder.tools.dir_ensure(dir_dest)
            if file:
                j.sal.fs.copyFile(src, dir_dest)
            else:
                j.sal.fs.copyDirTree(src, dir_dest)

    def write_files(self, files, dest):
        """write the files in <files> relative to <dest>

        :param files: a dict where the key is the path and the value is the content of the file
        :type files: dict
        :param dest: the root path to be appended to the paths in files
        :type dest: [str
        """
        for file_dest, content in files.items():
            file_dest = j.sal.fs.joinPaths(dest, self.tools.path_relative(file_dest))
            dir = j.sal.fs.getDirName(file_dest)
            j.builder.tools.dir_ensure(dir)
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
        self.copy_dirs(self.root_dirs, sandbox_dir)
        self.write_files(self.root_files, sandbox_dir)

        if self.startup:
            file_dest = j.sal.fs.joinPaths(sandbox_dir, '.startup.toml')
            j.builder.tools.file_ensure(file_dest)
            j.builder.tools.file_write(file_dest, self.startup)

        ld_dest = j.sal.fs.joinPaths(sandbox_dir, 'lib64/')
        j.builder.tools.dir_ensure(ld_dest)
        j.sal.fs.copyFile('/lib64/ld-linux-x86-64.so.2', ld_dest)

        self._log_info('building flist')
        tarfile = '/tmp/{}.tar.gz'.format(self.NAME)

        j.sal.process.execute('tar czf {} -C {} .'.format(tarfile, sandbox_dir))

        if hub_instance:
            if not j.clients.zhub._exists(name=hub_instance):
                raise j.exceptions.Input("hub instance %s does not exists, can't upload to the hub" % hub_instance)
            hub = j.clients.zhub.get(hub_instance)
            hub.authenticate()
            self._log_info("uploading flist to the hub")
            hub.upload(tarfile)
            self._log_info("uploaded at https://hub.grid.tf/{}/{}.flist".format(hub.username,
                                                                                   self.NAME))

        return tarfile
