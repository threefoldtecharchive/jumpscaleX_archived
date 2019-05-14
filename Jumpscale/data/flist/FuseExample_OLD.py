from collections import defaultdict
import errno
import pwd
import grp
import os
import stat
import llfuse
from time import time
import g8os_stor  # nim module to talk to ardb
from llfuse import FUSEError

from Jumpscale import j


try:
    import faulthandler
except ImportError:
    pass
else:
    faulthandler.enable()


class FuseOperations(llfuse.Operations):
    # {name: '', parent_inode: int, inode: int}
    contents = []
    # {inode: path}
    inode_path = {}
    inode_hash = {}
    inode_buffer = {}

    def __init__(self, rootpath):
        super().__init__()

        self.rootpath = rootpath
        self._flistmeta = j.tools.flist.getFlistMetadata(rootpath)
        self.init_data()
        self.max_inode_count = llfuse.ROOT_INODE
        self.client = g8os_stor.getClientId0("172.17.0.4", 16379)

    def init_data(self):
        self.inode_path[llfuse.ROOT_INODE] = self.rootpath
        content = {"name": "..", "parent_inode": llfuse.ROOT_INODE, "inode": llfuse.ROOT_INODE}
        self.contents.append(content)

    def lookup(self, inode_p, name, ctx=None):
        if name == ".":
            inode = inode_p
        elif name == "..":
            inode = self._get_parent_inode(inode_p)
        else:
            for content in self.contents:
                if inode_p == content["parent_inode"] and name.decode("utf-8") == content["name"]:
                    inode = content["inode"]
                    break
        try:
            inode_entry = self.getattr(inode, ctx)
        except UnboundLocalError:
            raise llfuse
        return inode_entry

    def getattr(self, inode, ctx=None):
        ppath = self.inode_path[inode]
        entity = self._flistmeta.getDirOrFile(ppath)
        entityAcl = self._flistmeta.aciCollection.get(entity["aclkey"]).dbobj

        entry = llfuse.EntryAttributes()
        entry.st_ino = inode
        entry.generation = 0
        entry.entry_timeout = 300
        entry.attr_timeout = 300
        entry.st_mode = entityAcl.mode
        entry.st_uid = pwd.getpwnam(entityAcl.uname).pw_uid
        entry.st_gid = grp.getgrnam(entityAcl.gname).gr_gid
        entry.st_size = entity["size"]

        entry.st_blksize = 4096

        entry.st_blocks = 0 if entity["size"] == 0 else int(((entity["size"] - 1) / entry.st_blksize + 1)) * 8
        entry.st_atime_ns = int(time() * 1e9)
        entry.st_mtime_ns = entity["modificationTime"] * 1e9
        entry.st_ctime_ns = entity["creationTime"] * 1e9

        return entry

    def opendir(self, inode, ctx):
        return inode

    def readdir(self, inode, off):
        entries = []
        ddir = self._flistmeta.getDirOrFile(self.inode_path[inode])

        # TODO: Refactor, Ugly
        for entry in ddir["dirs"]:
            subdir = self._flistmeta.dirCollection.get(entry["key"]).dbobj
            ppath = os.path.join(self.rootpath, subdir.location)
            if self.max_inode_count + 1 not in self.inode_path and ppath not in self.inode_path.values():
                self.max_inode_count += 1
                self.inode_path[self.max_inode_count] = os.path.join(self.rootpath, subdir.location)
                self.contents.append({"inode": self.max_inode_count, "parent_inode": inode, "name": subdir.name})
            entries.append(entry)

        for entry in ddir["files"]:
            ppath = os.path.join(self.rootpath, ddir["location"], entry["name"])
            if self.max_inode_count + 1 not in self.inode_path and ppath not in self.inode_path.values():
                self.max_inode_count += 1
                self.inode_path[self.max_inode_count] = os.path.join(self.rootpath, ddir["location"], entry["name"])
                self.contents.append({"inode": self.max_inode_count, "parent_inode": inode, "name": entry["name"]})
            entries.append(entry)

        for entry in ddir["links"]:
            ppath = os.path.join(self.rootpath, ddir["location"], entry["name"])
            if self.max_inode_count + 1 not in self.inode_path and ppath not in self.inode_path.values():
                self.max_inode_count += 1
                self.inode_path[self.max_inode_count] = os.path.join(self.rootpath, ddir["location"], entry["name"])
                self.contents.append({"inode": self.max_inode_count, "parent_inode": inode, "name": entry["name"]})
            entries.append(entry)

        for entry in ddir["specials"]:
            ppath = os.path.join(self.rootpath, ddir["location"], entry["name"])
            if self.max_inode_count + 1 not in self.inode_path and ppath not in self.inode_path.values():
                self.max_inode_count += 1
                self.inode_path[self.max_inode_count] = os.path.join(self.rootpath, ddir["location"], entry["name"])
                self.contents.append({"inode": self.max_inode_count, "parent_inode": inode, "name": entry["name"]})
            entries.append(entry)

        if off != 0 and off == len(entries):
            entries = []

        for idx, entry in enumerate(entries):
            for content in self.contents:
                if content["name"] == entry["name"] and content["parent_inode"] == inode:
                    entry_inode = content["inode"]
            yield (bytes(entry["name"], "utf-8"), self.getattr(entry_inode), idx + 1)

    def _get_parent_inode(self, inode):
        for content in self.contents:
            if inode == content["inode"]:
                return content["parent_inode"]

    def open(self, inode, flags, ctx):
        return inode

    def read(self, fh, offset, length):
        ppath = "/tmp/{}".format(j.sal.fs.getBaseName(self.inode_path[fh]))
        g8os_stor.downloadFile0(self.client, ppath, self.inode_hash[fh])
        with open(ppath, "rb") as f:
            data = f.read()
        j.sal.fs.remove(ppath)
        return data[offset : offset + length]

    def create(self, inode_parent, name, mode, flags, ctx):
        self.max_inode_count += 1
        name = name.decode("utf-8")
        content = {"name": name, "parent_inode": inode_parent, "inode": self.max_inode_count}
        self.contents.append(content)
        parent_path = self.inode_path[inode_parent]
        self.inode_path[self.max_inode_count] = os.path.join(parent_path, name)
        if stat.S_ISDIR(mode):
            self._flistmeta.mkdir(parent_path, name)
        else:
            self._flistmeta.addFile(parent_path, name)
        return (self.max_inode_count, self.getattr(self.max_inode_count))

    def write(self, fh, offset, buf):
        data = self.inode_buffer.get(fh, None)
        if data is None:
            data = b""
        data = data
        data = data[:offset] + buf + data[offset + len(buf) :]
        self.inode_buffer[fh] = data
        return len(buf)

    def release(self, fh):
        data = None
        if self.inode_buffer.get(fh, None):
            ppath = "/tmp/{}".format(j.sal.fs.getBaseName(self.inode_path[fh]))
            if self.inode_hash.get(fh, None):
                g8os_stor.downloadFile0(self.client, ppath, self.inode_hash[fh])
                with open(ppath) as f:
                    data = f.read()

            with open(ppath, "wb") as f:
                if data is None:
                    data = self.inode_buffer.pop(fh)
                else:
                    data = bytes(data, "utf-8") + self.inode_buffer[fh]
                f.write(data)
            self.inode_hash[fh] = g8os_stor.uploadFile0(self.client, ppath, 0)
            j.sal.fs.remove(ppath)


class FuseExample(llfuse.Operations):
    def __init__(self, rootpath):
        MOUNT_POINT = "/tmp/mountpoint"
        ops = FuseOperations(rootpath)
        fuse_options = set(llfuse.default_options)
        fuse_options.add("fsname=testfs")
        fuse_options.discard("default_permissions")
        j.sal.fs.createDir(MOUNT_POINT)
        llfuse.init(ops, MOUNT_POINT, fuse_options)
        try:
            llfuse.main(workers=1)
        except BaseException:
            llfuse.close(unmount=False)
            raise
        llfuse.close()
