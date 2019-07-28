from Jumpscale import j

JSBASE = j.application.JSBaseClass


class BCDBFS(j.application.JSBaseClass):
    """
    A sal for BCDB File System
    BCDB file system is a file system where everything is stored in bcdb
    """

    __jslocation__ = "j.sal.bcdbfs"

    def _init(self, bcdb_name="bcdbfs"):
        self.bcdb = j.data.bcdb.get(bcdb_name)
        self._file_model = self.bcdb.model_get_from_url("jumpscale.bcdb.fs.file.2")
        self._dir_model = self.bcdb.model_get_from_url("jumpscale.bcdb.fs.dir.2")

    #############################
    ######  DIR OPERATIONS ######
    #############################
    def mkdir(self, path):
        """
        create a directory
        :param path: full path of the directory
        :return: Directory object
        """
        return self._dir_model.create_empty_dir(path)

    def rmdir(self, path, recursive=True):
        """
        Remove directory
        :param path: directory path
        :param recursive: if true will perform recursive delete by deleting all sub directorie
        :return: None
        """
        dir = self._dir_model.get(name=path)
        if not recursive and dir.dirs:
            raise RuntimeError("this dir contains other dirs you must pass recursive = True")
        elif not recursive and not dir.dirs:
            for file_id in dir.files:
                file = self._file_model.get(file_id)
                file.delete()
            dir.files = []
            dir.save()
        elif recursive:
            self._dir_model.delete_recursive(path)

    def dir_copy_from_local(self, path, dest, recursive=True):
        """
        copy directory from local file system to bcdb
        :param path: full path of the directory (the directory must exist on the local file system)
        :param dest: dest to copy the dir to on bcdbfs
        :param recursive: copy subdirs
        :return:
        """
        source_files = j.sal.fs.listFilesInDir(path)
        for file in source_files:
            basename = j.sal.getBaseName(file)
            self.file_copy_from_local(file, j.sal.fs.joinPaths(path, basename))
        if recursive:
            source_dirs = j.sal.fs.listDirsInDir(path)
            for dir in source_dirs:
                self.mkdir(dir)
                basename = j.sal.fs.getBaseName(dir)
                self.dir_copy_from_local(dir, j.sal.fs.joinPaths(dest, basename))

    def dir_copy_from_bcdbfs(self, path, dest, recursive=True):
        """
        copy directory from a location in bcdbfs file system to another
        :param path: full path of the directory (the directory must exist in bcdbfs)
        :param dest: dest to copy the dir to on bcdbfs
        :param recursive: copy subdirs
        :return:
        """
        dir_source = self._dir_model.get(name=path)
        source_files = dir_source.files
        for file_id in source_files:
            file = self._file_model.get(file_id)
            basename = j.sal.getBaseName(file.name)
            self.file_copy_form_bcdbfs(file.path, j.sal.fs.joinPaths(path, basename))
        if recursive:
            source_dirs = dir_source.dirs
            for dir_id in source_dirs:
                dir = self._dir_model.get(dir_id)
                self.mkdir(dir.name)
                basename = j.sal.fs.getBaseName(dir.name)
                self.dir_copy_from_bcdbfs(dir.name, j.sal.fs.joinPaths(dest, basename))

    def dir_copy(self, path, dest, recursive=True):
        """
        copies a dir from either local file system or from bcdbfs
        :param path: source path
        :param dest: destination
        :param recursive: copy subdirs
        :return:
        """
        if j.sal.fs.exists(path):
            self.dir_copy_from_local(path, dest, recursive=recursive)
        else:
            self.dir_copy_from_bcdbfs(path, dest, recursive=recursive)

    #############################
    ###### FILE OPERATIONS ######
    #############################
    def file_create_empty(self, filename):
        """
        Creates empty file
        :param filename: full file path
        :return: file object
        """
        return self._file_model.file_create_empty(filename)

    def file_write(self, filename, contents, append=True, create=True):
        """
        writes a file to bcdb
        :param path: the path to store the file
        :param content: content of the file to be written
        :param append: if True will append if the file already exists
        :param create: create new if true and the file doesn't exist
        :return: file object
        """
        return self._file_model.file_create_empty(filename, contents, append=append, create=create)

    def file_copy_from_local(self, path, dest):
        """
        copies file from local file system to bcdb
        :param path: path on local file system
        :param dest: destination on bcdbfs
        :return: file object
        """
        if not j.sal.fs.exists(path):
            raise RuntimeError("{} doesn't exist on local file system".format(path))
        content = open(path)
        return self.file_write(dest, content, append=False, create=True)

    def file_copy_form_bcdbfs(self, path, dest):
        """
        copies file to another location in bcdbfs
        :param path: full path of the file
        :param dest: destination path
        :return: file object
        """
        source_file = self._file_model.get(name=path)
        dest_file = self.file_create_empty(dest)
        if source_file.blocks:
            dest_file.blocks = source_file.blocks
        elif source_file.content:
            dest_file.content = source_file.content

        dest_file.save()
        return dest_file

    def file_copy(self, path, dest):
        """
        copies file either from the local file system or from another location in bcdbfs
        :param path: full path to the file
        :param dest: destination path
        :return: file object
        """
        # first check if path exists on the file system
        if j.sal.fs.exists(path):
            return self.file_copy_from_local(path, dest)
        else:
            return self.file_copy_form_bcdbfs(path, dest)

    def file_delete(self, path):
        return self._file_model.file_delete(path)

    def _destroy(self):
        """
        VERY DANGEROUS: deletes everything in bcdbfs
        :return:
        """

    def test(self):
        j.shell()
        for i in range(5):
            j.sal.bcdbfs.mkdir("/dir_{}".format(i))
