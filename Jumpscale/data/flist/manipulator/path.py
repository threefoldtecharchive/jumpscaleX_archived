import fnmatch
import os
from stat import S_ISBLK, S_ISCHR, S_ISFIFO, S_ISLNK, S_ISREG, S_ISSOCK
import pwd
import grp

import g8storclient
from Jumpscale import j


class Path:
    def __init__(self, obj, parent, flist):
        self._obj = obj
        self._parent = parent
        self._flist = flist

    def __repr__(self):
        if hasattr(self._obj, "contents"):
            ttype = "dir"
        else:
            ttype = str(self._obj.attributes.which())
        return "%s(%s)" % (ttype, self.name)

    @property
    def abspath(self):
        """
        see os.path.abspath()
        """
        if self._parent is None:
            return self._flist.rootpath

        if self._parent.abspath == "":
            raise j.exceptions.Base("a file should always have a parent location")

        return os.path.join(self._parent.abspath, self.name)

    @property
    def mtime(self):
        """
        Last modification time of the file.
        """
        return self._obj.modificationTime

    @property
    def ctime(self):
        """
        creation time of the file.
        """
        return self._obj.creationTime

    @property
    def basename(self):
        """
        see os.path.basename()
        """
        parent = getattr(self._obj, "parent", None)
        if parent == "":  # root directory
            return self._flist.rootpath

        # case for file,link,specials
        return self._obj.name

    @property
    def name(self):
        """
        see basename
        """
        return self.basename

    @property
    def size(self):
        """
        Size of the file, in bytes.
        """
        return self._obj.size

    @property
    def stem(self):
        """
        The same as name(), but with one file extension stripped off.
        """
        return os.path.splitext(self.basename)

    def chmod(self, mode):
        """
        see os.chmod()
        """
        raise j.exceptions.NotImplemented()

    def copy(self, src, follow_symlinks=True):
        """
        copy a file from the local filesystem into the flist
        """
        self._log_debug("copy file from %s to %s", src, os.path.join(self.abspath, os.path.basename(src)))
        return self._add_file(src)

    def copytree(self, src):
        """
        Recursively copy a directory tree.
        """
        if not os.path.isdir(src):
            raise j.exceptions.Value("src must be a directory")

        def find_dir(location):
            current = self
            for dir_name in location.split(os.path.sep)[2:]:
                try:
                    current = current.dirs(dir_name)[0]
                except IndexError:
                    current = current.mkdir(dir_name)
            return current

        for dirpath, dirnames, filenames in os.walk(src):
            flit_dir = find_dir(dirpath)
            for name in dirnames:
                flit_dir.mkdir(name)
            for name in filenames:
                flit_dir.copy(os.path.join(dirpath, name))

    def mkdir(self, name, mode="511"):
        """
        create a new directory
        """
        dir = self._add_dir(name)
        self._log_debug("create directory at %s", dir.abspath)
        return dir

    def files(self, pattern=None):
        """
        list files in this directory

        The elements of the list are Path objects. This does not walk recursively into subdirectories (but see walkdirs()).

        With the optional pattern argument, this only lists directories whose names match the given pattern. For example, d.dirs('build-*').
        """
        return self._filter_content("file")

    def dirs(self, pattern=None):
        """
        List of this directory's subdirectories.

        The elements of the list are Path objects. This does not walk recursively into subdirectories (but see walkdirs()).

        With the optional pattern argument, this only lists directories whose names match the given pattern. For example, d.dirs('build-*').
        """
        return self._filter_content("dir", pattern)

    def links(self, pattern=None):
        """
        List of this directory's links.

        The elements of the list are Path objects. This does not walk recursively into subdirectories (but see walkdirs()).

        With the optional pattern argument, this only lists directories whose names match the given pattern. For example, d.dirs('build-*').
        """
        return self._filter_content("link", pattern)

    def specials(self, pattern=None):
        """
        List of this directory's special files.

        The elements of the list are Path objects. This does not walk recursively into subdirectories (but see walkdirs()).

        With the optional pattern argument, this only lists directories whose names match the given pattern. For example, d.dirs('build-*').
        """
        return self._filter_content("special", pattern)

    def glob(self, pattern):
        """
        Return a list of Path objects that match the pattern.

        pattern - a path relative to this directory, with wildcards.

        For example, Path('/users').glob('*/bin/*') returns a list of all the files users have in their bin directories.
        """
        raise j.exceptions.NotImplemented()

    def link(self, newpath):
        """
        Create a hard link at newpath, pointing to this file.

        See also

        os.link()
        """
        raise j.exceptions.NotImplemented()

    def unlink(self):
        """
        See also

        os.unlink()
        """
        raise j.exceptions.NotImplemented()

    def move(self, dst):
        """
        Recursively move a file or directory to another location. This is similar to the Unix “mv” command. Return the file or directory’s destination.

        If the destination is a directory or a symlink to a directory, the source is moved inside the directory. The destination path must not already exist.

        If the destination already exists but is not a directory, it may be overwritten depending on os.rename() semantics.

        If the destination is on our current filesystem, then rename() is used. Otherwise, src is copied to the destination and then removed. Symlinks are recreated under the new name if os.rename() fails because of cross filesystem renames.

        The optional copy_function argument is a callable that will be used to copy the source or it will be delegated to copytree. By default, copy2() is used, but any function that supports the same signature (like copy()) can be used.

        A lot more could be done here… A look at a mv.c shows a lot of the issues this implementation glosses over.
        """
        raise j.exceptions.NotImplemented()

    @property
    def parent(self):
        """
        This path’s parent directory, as a new Path object.

        For example, Path('/usr/local/lib/libpython.so').parent == Path('/usr/local/lib')
        """
        return self._parent

    def remove(self):
        """
        remove
        """
        raise j.exceptions.NotImplemented()

    def rename(self):
        """
        rename
        """
        raise j.exceptions.NotImplemented()

    def _filter_content(self, ttype, pattern=None):
        if not hasattr(self._obj, "contents"):
            return []

        if ttype not in ("file", "dir", "link", "special"):
            raise j.exceptions.Value("type should be one of 'file','dir', 'link','special'")
        out = []

        for x in self._obj.contents:
            if x.attributes.which() != ttype:
                continue
            if pattern and not fnmatch.fnmatch(x.name, pattern):
                continue
            if ttype == "dir":
                x = self._flist.dirCollection.get(x.attributes.dir.key).dbobj

            out.append(Path(obj=x, parent=self, flist=self._flist))
        return out

    def _add_dir(self, name):
        _, self_key = self._flist.path2key(self.abspath)

        # create the new directory object
        _, dir_sub_key = self._flist.path2key(os.path.join(self.abspath, name))
        new_dir = self._flist.dirCollection.get(dir_sub_key, autoCreate=True)
        new_dir.dbobj.name = name
        new_dir.dbobj.location = self.abspath
        new_dir.dbobj.parent = self_key
        new_dir.dbobj.aclkey = self._obj.aclkey
        now = j.data.time.epoch
        new_dir.dbobj.modificationTime = now
        new_dir.dbobj.creationTime = now
        new_dir.save()

        # add new inode into the contents of the current directory
        new_inode = self._new_inode()
        new_inode.name = name
        new_inode.size = 0
        new_inode.aclkey = self._obj.aclkey
        new_inode.modificationTime = j.data.time.epoch
        new_inode.creationTime = new_inode.modificationTime
        new_inode.attributes.dir = new_inode.attributes.init("dir")
        new_inode.attributes.dir.key = dir_sub_key

        self._obj.modificationTime = now
        model = self._flist.dirCollection.get(self_key)
        model.dbobj = self._obj
        model.save()

        return Path(new_dir.dbobj, self, self._flist)

    def _add_file(self, src):
        if os.path.isdir(src):
            raise j.exceptions.Value("src must be a file (%s)" % src)

        _, self_key = self._flist.path2key(self.abspath)

        src_stat = os.stat(src, follow_symlinks=False)

        # add new inode into the contents of the current directory
        new_inode = self._new_inode()
        new_inode.name = os.path.basename(src)
        new_inode.size = src_stat.st_size
        new_inode.modificationTime = int(src_stat.st_mtime)
        new_inode.creationTime = int(src_stat.st_ctime)

        if S_ISLNK(src_stat.st_mode):
            # Checking absolute path, relative may fail
            new_inode.attributes.link = new_inode.attributes.init("link")
            new_inode.attributes.link.target = os.readlink(src)
        elif S_ISREG(src_stat.st_mode):
            new_inode.attributes.file = new_inode.attributes.init("file")
            new_inode.attributes.file.blockSize = 128  # FIXME ?
            fullpath = os.path.abspath(src)
            self._log_debug("[+] populating: %s" % fullpath)
            hashs = g8storclient.encrypt(fullpath)

            if hashs is None:
                return

            for index, value in enumerate(hashs):
                hashs[index].pop("data", None)

            new_inode.attributes.file.blocks = hashs
            # keep the path of the added file, so we can upload the content of the file on the backend
            # once we're done editing the flist
            self._flist._added_files.add(src)
        else:
            # special file
            new_inode.attributes.special = new_inode.attributes.init("special")
            if S_ISSOCK(src_stat.st_mode):
                new_inode.attributes.special.type = "socket"
            elif S_ISBLK(src_stat.st_mode):
                new_inode.attributes.special.type = "block"
            elif S_ISCHR(src_stat.st_mode):
                new_inode.attributes.special.type = "chardev"
            elif S_ISFIFO(src_stat.st_mode):
                new_inode.attributes.special.type = "fifopipe"
            else:
                new_inode.attributes.special.type = "unknown"

            if S_ISBLK(src_stat.st_mode) or S_ISCHR(src_stat.st_mode):
                id = "%d,%d" % (os.major(src_stat.st_rdev), os.minor(src_stat.st_rdev))
                new_inode.attributes.special.data = id

        # set ACI on new inode
        uname = str(src_stat.st_uid)
        gname = str(src_stat.st_gid)
        # ignore if the username/groupname is not found on host
        try:
            uname = pwd.getpwuid(src_stat.st_uid).pw_name
            gname = grp.getgrgid(src_stat.st_gid).gr_name
        except Exception:
            pass

        aci = self._flist.aciCollection.new()
        aci.dbobj.uname = uname
        aci.dbobj.gname = gname
        aci.dbobj.mode = src_stat.st_mode
        if not self._flist.aciCollection.exists(aci.key):
            aci.save()
        new_inode.aclkey = aci.key

        self._obj.modificationTime = j.data.time.epoch
        model = self._flist.dirCollection.get(self_key)
        model.dbobj = self._obj
        model.save()

        return Path(new_inode, self, self._flist)

    def _new_inode(self):
        prev_content = [x.copy() for x in self._obj.contents]
        contents = self._obj.init("contents", len(self._obj.contents) + 1)

        for i, x in enumerate(prev_content):
            # copy old content over
            contents[i] = x

        return contents[-1]
