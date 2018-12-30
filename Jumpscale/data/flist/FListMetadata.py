from Jumpscale import j
import pyblake2
import binascii
import os
import calendar
import time
import stat
import pwd
import grp
JSBASE = j.application.JSBaseClass


class FListMetadata(j.application.JSBaseClass):
    """Metadata layer on top of flist that enables flist manipulation"""

    def __init__(
            self,
            namespace="main",
            rootpath="/",
            dirCollection=None,
            aciCollection=None,
            userGroupCollection=None):
        JSBASE.__init__(self)
        self.namespace = namespace
        self.dirCollection = dirCollection
        self.aciCollection = aciCollection
        self.userGroupCollection = userGroupCollection
        self.rootpath = rootpath

    def getDirOrFile(self, ppath):
        """
        :param ppath: path of directory or file
        :return: dict of dirctory object, in case of file path it returns parent directory of that file
        """
        fType, dirObj = self._search_db(ppath)
        if dirObj.dbobj.state != "":
            raise RuntimeError("%s: No such file or directory" % ppath)

        if fType == "D" and dirObj.dbobj.location == ppath[len(
                self.rootpath):].strip("/"):
            return dirObj.dbobj.to_dict()
        else:
            file_name = j.sal.fs.getBaseName(ppath)
            _, propList = self._getPropertyList(dirObj.dbobj, fType)
            for file in propList:
                if file.name == file_name:
                    if fType == "D":
                        return self.dirCollection.get(file.key).dbobj.to_dict()
                    return file.to_dict()
            return file.to_dict()

    def mkdir(self, parent_path, name, mode="755"):
        """
        :param param_name:
        :return:
        """
        ppath = j.sal.fs.joinPaths(parent_path, name)
        dirRelPath, dirKey = self._path2key(ppath)
        if self.dirCollection.exists(dirKey):
            raise RuntimeError(
                "cannot create directory '%s': File exists" % ppath)
        dirObj = self.dirCollection.get(dirKey, autoCreate=True)

        _, dirKeyParent = self._path2key(parent_path)
        parentObj = self.dirCollection.get(dirKeyParent)
        if parentObj.dbobj.state != "":
            raise RuntimeError("%s: No such file or directory" % ppath)

        aciKey = self._initialize_aci(mode, stat.S_IFDIR)
        # Initialize dirObj
        dirObj.dbobj.name = name
        dirObj.dbobj.location = dirRelPath
        dirObj.dbobj.creationTime = calendar.timegm(time.gmtime())
        dirObj.dbobj.modificationTime = calendar.timegm(time.gmtime())
        dirObj.dbobj.aclkey = aciKey
        dirObj.dbobj.dirs = []
        dirObj.dbobj.files = []
        dirObj.dbobj.links = []
        dirObj.dbobj.specials = []
        dirObj.dbobj.size = 0
        dirObj.dbobj.parent = dirKeyParent
        dirObj.dbobj.isLink = False
        dirObj.save()

        # add dir to parent directory
        dirProps = {"key": dirKey, "name": name}
        self._addObj(parentObj, dirProps, "D")
        parentObj.save()

    def addFile(self, parent_path, name, size=0, mode="644"):
        _, parentObj = self._search_db(parent_path)
        if parentObj.dbobj.state != "":
            raise RuntimeError("%s: No such file or directory" % parent_path)

        aciKey = self._initialize_aci(mode, stat.S_IFREG)
        fileDict = {
            "aclkey": aciKey,
            "blocksize": size,
            "creationTime": calendar.timegm(time.gmtime()),
            "modificationTime": calendar.timegm(time.gmtime()),
            "name": name,
            "size": size,
        }
        self._addObj(parentObj, fileDict, "F")
        parentObj.save()

    def link(self, ppath, parent_path, file_type="s"):
        if file_type not in ("s", "h"):
            raise j.exceptions.Input(message="file_type must be 's' or 'h")

        _, parentObj = self._search_db(parent_path)
        if parentObj.dbobj.state != "":
            raise RuntimeError("%s: No such file or directory" % parent_path)

        if parent_path == j.sal.fs.getDirName(ppath):
            raise RuntimeError("Cannot link to file to itself")

        relpath = ppath[len(self.rootpath):].strip("/")
        for link in parentObj.dbobj.links:
            if link.target == relpath:
                raise j.exceptions.Input(message="Link already exists")

        linkDict = {
            "name": j.sal.fs.getBaseName(ppath),
            "creationTime": calendar.timegm(time.gmtime()),
            "modificationTime": calendar.timegm(time.gmtime()),
            "target": relpath
        }
        self._addObj(parentObj, linkDict, "L")
        parentObj.save()

    def chown(self, ppath, gname, uname):
        fType, dirObj = self._search_db(ppath)
        if dirObj.dbobj.state != "":
            raise RuntimeError("%s: No such file or directory" % ppath)

        if fType == "D":
            aclObj = self.aciCollection.get(dirObj.dbobj.aclkey)
            aclObj.dbobj.gname = gname
            aclObj.dbobj.uname = uname
            aclObj.save()
        else:
            _, propList = self._getPropertyList(dirObj.dbobj, fType)
            for file in propList:
                if file.name == j.sal.fs.getBaseName(ppath):
                    aclObj = self.aciCollection.get(file.aclkey)
                    aclObj.dbobj.gname = gname
                    aclObj.dbobj.uname = uname
                    aclObj.save()

    def chmod(self, ppath, mode):
        """
        Change mode for files or directories
        :param ppath: path of file/dir
        :param mode: string of the mode

        Examples:
        flistmeta.chmod("/tmp/dir1", "777")
        """
        fType, dirObj = self._search_db(ppath)
        if dirObj.dbobj.state != "":
            raise RuntimeError("%s: No such file or directory" % ppath)

        try:
            mode = int(mode, 8)
        except ValueError:
            raise ValueError("Invalid mode.")
        else:
            if fType == "D":
                _mode = mode + stat.S_IFDIR
                aclObj = self.aciCollection.get(dirObj.dbobj.aclkey)
                aclObj.dbobj.mode = _mode
                aclObj.save()

            elif fType == "F" or fType == "L":
                _mode = mode + stat.S_IFREG if fType == "F" else mode + stat.S_IFLNK
                _, propList = self._getPropertyList(dirObj.dbobj, fType)
                for file in propList:
                    if file.name == j.sal.fs.getBaseName(ppath):
                        aclObj = self.aciCollection.get(file.aclkey)
                        aclObj.dbobj.mode = _mode
                        aclObj.save()
            else:
                for file in dirObj.dbobj.links:
                    if file.name == j.sal.fs.getBaseName(ppath):
                        aclObj = self.aciCollection.get(file.aclkey)
                        if stat.S_ISSOCK(aclObj.dbobj.st_mode):
                            _mode = mode + stat.S_IFSOCK
                        elif stat.S_ISBLK(aclObj.dbobj.st_mode):
                            _mode = mode + stat.S_IFBLK
                        elif stat.S_ISCHR(aclObj.dbobj.st_mode):
                            _mode = mode + stat.S_IFCHR
                        elif stat.S_ISFIFO(aclObj.dbobj.st_mode):
                            _mode = mode + stat.S_IFIFO
                        aclObj.dbobj.mode = _mode
                        aclObj.save()

    def delete(self, ppath):
        fType, dirObj = self._search_db(ppath)
        if dirObj.dbobj.state != "":
            raise RuntimeError("%s: No such file or directory" % ppath)

        if fType == "D":
            dbobj = dirObj.dbobj
            if len(
                dbobj.dirs) != 0 and len(
                dbobj.files) != 0 and len(
                dbobj.links) != 0 and len(
                    dbobj.specials) != 0:
                raise RuntimeError(
                    "failed to remove '%s': Directory not empty" % ppath)
            dirObj.dbobj.state = "Deleted"
        else:
            _, entityList = self._getPropertyList(dirObj.dbobj, fType)
            for entity in entityList:
                if entity.name == j.sal.fs.getBaseName(ppath):
                    entity.state = "Deleted"
        dirObj.save()

    def stat(self, ppath):
        fType, dirObj = self._search_db(ppath)
        stat = {}

        if dirObj.dbobj.state != "":
            raise RuntimeError("%s: No such file or directory" % ppath)

        if fType == "D":
            stat["modificationTime"] = dirObj.dbobj.modificationTime
            stat["size"] = dirObj.dbobj.size
            stat["creationTime"] = dirObj.dbobj.creationTime
        else:
            _, entityList = self._getPropertyList(dirObj.dbobj, fType)
            for entity in entityList:
                if entity.name == j.sal.fs.getBaseName(ppath):
                    stat["modificationTime"] = entity.modificationTime
                    stat["size"] = entity.size
                    stat["creationTime"] = entity.creationTime
                    # stat["blocksize"] = entity.blocksize # FIXME
        return stat

    def move(self, old_path, new_parent_path, fname=""):
        """
        Move/Rename files or directories
        :param old_path: path of files/dirs to be moved
        :param new_parent_path: path of the new parent directory
        :param fname: file name if desired to rename the entity

        Examples:
        ## Move directory:
        flistmeta.move("/tmp/dir/subdir", "/tmp/dir/subdir2")
        ## Rename directory
        flistmeta.move("/tmp/dir/subdir", "/tmp/dir/subdir", "subdir3")
        ## Move file
        flistmeta.move("/tmp/dir/subdir/sample.txt", "/tmp/dir/subdir2")
        ## Rename file
        flistmeta.move("/tmp/dir/subdir/sample.txt", "/tmp/dir/subdir", "sample2.txt")
        """
        oldFtype, oldDirObj = self._search_db(old_path)
        newFtype, newParentDirObj = self._search_db(new_parent_path)
        oldFName = j.sal.fs.getBaseName(old_path)
        fname = fname if fname else oldFName

        if oldFtype == "D":
            if "{}/".format(old_path) in new_parent_path:
                raise RuntimeError(
                    "Cannot move '{}' to a subdirectory of itself, '{}'".format(
                        old_path, new_parent_path))

            if oldDirObj.dbobj.state != "":
                raise RuntimeError("%s: No such file or directory" % old_path)

            _, parentDir = self._search_db(j.sal.fs.getDirName(old_path))
            self._move_dir(parentDir, newParentDirObj, oldDirObj, fname=fname)
        else:
            self._move_file(
                oldDirObj,
                newParentDirObj,
                oldFName,
                fname,
                oldFtype)

    def _move_dir(self, parentDir, newParentDirObj, dirObj, fname):
        if parentDir.key != newParentDirObj.key:
            dirProps = self._removeObj(parentDir, dirObj.dbobj.name, "D")
            dirProps["name"] = fname
            self._addObj(newParentDirObj, dirProps, "D")
            dirObj.dbobj.location = os.path.join(
                newParentDirObj.dbobj.location, fname)
            dirObj.dbobj.name = fname
            dirObj.dbobj.parent = newParentDirObj.key

            _, dirKey = self._path2key(
                os.path.join(
                    self.rootpath, newParentDirObj.dbobj.location, fname))
            ddir = self.dirCollection.get(dirKey, autoCreate=True)
            ddir.dbobj = dirObj.dbobj
            ddir.save()
            dirObj.dbobj.state = "Moved"
        elif dirObj.dbobj.name != fname:  # Rename only
            for dir in parentDir.dbobj.dirs:
                if dir.name != dirObj.dbobj.name:
                    dir.name = fname
            dirObj.dbobj.location = os.path.join(
                newParentDirObj.dbobj.location, fname)
            dirObj.dbobj.name = fname
            # Save new dir object
            _, dirKey = self._path2key(
                self.rootpath, os.path.join(
                    newParentDirObj.dbobj.location, fname))
            ddir = self.dirCollection.get(dirKey, autoCreate=True)
            ddir.dbobj = dirObj.dbobj
            ddir.save()
            dirObj.dbobj.state = "Moved"
        parentDir.save()
        newParentDirObj.save()
        dirObj.save()

    def _move_file(self, parentDir, newParentDirObj, oldFName, fname, ftype):
        if parentDir.key != newParentDirObj.key:
            fileProps = self._removeObj(parentDir, oldFName, ftype)
            fileProps["name"] = fname
            self._addObj(newParentDirObj, fileProps, ftype)
        elif oldFName != fname:
            for file in parentDir.dbobj.files:
                if oldFName != fname:
                    file.name = fname
                    file.modificationTime = calendar.timegm(time.gmtime())
        parentDir.save()
        newParentDirObj.save()

    def _removeObj(self, dirObj, name, ptype):
        newFiles = []
        poppedFile = {}
        pName, pList = self._getPropertyList(dirObj.dbobj, ptype)
        for file in pList:
            if file.name == name:
                poppedFile = file.to_dict()
            else:
                newFiles.append(file.to_dict())

        if poppedFile == {}:
            raise RuntimeError(
                "cannot remove '%s': No such file or directory" % dirObj.dbobj.location)

        newlist = dirObj.dbobj.init(pName, len(newFiles))
        for i, item in enumerate(newFiles):
            newlist[i] = item
        return poppedFile

    def _addObj(self, dirObj, fileProps, ptype):
        pName, pList = self._getPropertyList(dirObj.dbobj, ptype)
        newFiles = [item.to_dict() for item in pList]
        newFiles.append(fileProps)
        newlist = dirObj.dbobj.init(pName, len(newFiles))
        for i, item in enumerate(newFiles):
            newlist[i] = item

    def _getPropertyList(self, dbobj, ptype):
        if ptype == "D":
            return "dirs", dbobj.dirs
        if ptype == "F":
            return "files", dbobj.files
        if ptype == "L":
            return "links", dbobj.links
        if ptype == "S":
            return "specials", dbobj.specials

    def _search_db(self, ppath):
        """
        Search for file or directory through the database
        @return if ppath is file then it'll return directory containing the file
                else it'll return the dir
        """
        absolutePath = self._get_absolute_path(ppath)
        try:
            return "D", self._get_dir_from_db(absolutePath)
        except BaseException:            # Means that ppath is a file or doesn't exist
            baseName = j.sal.fs.getBaseName(absolutePath)
            parent_dir = j.sal.fs.getDirName(absolutePath)
            parent_dir_obj = self._get_dir_from_db(parent_dir)

            # Search for file in parent_dir
            for index, file in enumerate(parent_dir_obj.dbobj.files):
                if file.name == baseName:
                    return "F", parent_dir_obj

            # Search for links
            for index, link in enumerate(parent_dir_obj.dbobj.links):
                if link.name == baseName:
                    return "L", parent_dir_obj

            # Search for links
            for index, special in enumerate(parent_dir_obj.dbobj.specials):
                if special.name == baseName:
                    return "S", parent_dir_obj

            raise RuntimeError("%s: No such file or directory" % absolutePath)

    def _get_dir_from_db(self, dirPath):
        _, key = self._path2key(dirPath)
        return self.dirCollection.get(key)

    def _get_absolute_path(self, path):
        if path.startswith(self.rootpath):
            return os.path.join(self.rootpath, path)
        return path

    def _path2key(self, fpath):
        """
        @param fpath is full path
        """
        if not fpath.startswith(self.rootpath):
            raise j.exceptions.Input(
                message="fpath:%s needs to start with rootpath:%s" % (fpath, self.rootpath))
        relPath = fpath[len(self.rootpath):].strip("/")
        toHash = self.namespace + relPath
        self._logger.debug("> %s" % toHash)
        bl = pyblake2.blake2b(toHash.encode(), 32)
        binhash = bl.digest()
        self._logger.debug(binascii.hexlify(binhash).decode())
        return relPath, binascii.hexlify(binhash).decode()

    def _initialize_aci(self, mode, fileType):
        valid_types = [
            stat.S_IFREG,
            stat.S_IFDIR,
            stat.S_IFCHR,
            stat.S_IFBLK,
            stat.S_IFIFO,
            stat.S_IFLNK,
            stat.S_IFSOCK]
        if fileType not in valid_types:
            raise RuntimeError("Invalid file type.")

        aci = self.aciCollection.new()
        uid = os.getuid()
        aci.dbobj.id = uid
        aci.dbobj.uname = pwd.getpwuid(uid).pw_name
        aci.dbobj.gname = grp.getgrgid(os.getgid()).gr_name
        aci.dbobj.mode = int(mode, 8) + fileType
        aci.save()
        return aci.key
