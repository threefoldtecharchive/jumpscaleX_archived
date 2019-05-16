from Jumpscale import j
import capnp
from . import model_capnp as ModelCapnp


class FlistMerger:
    """
        Tool to merge multiple flist into one

        How to use:

        kvs = j.data.kvs.getRocksDBStore(name='flist', namespace=None, dbpath="/tmp/jumpcale.db")
        fjs = j.tools.flist.getFlist(rootpath='/tmp/rootB', kvs=kvs)
        fjs.add('/tmp/rootB')

        kvs = j.data.kvs.getRocksDBStore(name='flist', namespace=None, dbpath="/tmp/ardb.db")
        fardb = j.tools.flist.getFlist(rootpath='/tmp/rootA', kvs=kvs)
        fardb.add('/tmp/rootA')

        kvs = j.data.kvs.getRocksDBStore(name='flist', namespace=None, dbpath="/tmp/merge.db")
        fdest = j.tools.flist.getFlist(rootpath='/', kvs=kvs)

        merger = j.tools.flist.get_merger()
        merger.add_source(fjs)
        merger.add_source(fardb)
        merger.add_destination(fdest)
        merger.merge()

        fdest.pprint()
    """

    def __init__(self):
        self._sources = []
        self._dest = None

    def add_source(self, flist):
        self._sources.append(flist)

    def add_destination(self, flist):
        self._dest = flist
        # make sure the root directory exists in the destination flist
        _, key = self._dest.path2key(self._dest.rootpath)
        if not self._dest.dirCollection.exists(key):
            root_dir = self._dest.dirCollection.new()
            root_dir.dbobj.creationTime = j.data.time.epoch
            root_dir.dbobj.creationTime = root_dir.dbobj.creationTime
            root_dir.dbobj.name = "/"
            root_dir.key = key
            root_dir.save()

    def merge(self):
        # TODO: handle conflicting files
        for src_fs in self._sources:
            src_fs.walk(
                dirFunction=dirFunction,
                fileFunction=fileFunction,
                linkFunction=linkFunction,
                specialFunction=specialFunction,
                args={"src_fs": src_fs, "dest_fs": self._dest},
            )


def dest_parent_dir(dest_fs, src_dirobj):
    _, dest_parent_key = dest_fs.path2key(
        j.sal.fs.joinPaths(dest_fs.rootpath, j.sal.fs.getParent(src_dirobj.dbobj.location) or dest_fs.rootpath)
    )
    return dest_fs.dirCollection.get(dest_parent_key)


def dest_current_dir(dest_fs, src_dirobj):
    _, dest_parent_key = dest_fs.path2key(j.sal.fs.joinPaths(dest_fs.rootpath, src_dirobj.dbobj.location))
    return dest_fs.dirCollection.get(dest_parent_key)


def dirFunction(dirobj, type, name, args, key):
    dest_fs = args["dest_fs"]
    src_fs = args["src_fs"]

    # get current directory of source filesystem
    src_dir = src_fs.dirCollection.get(key)
    # get current directory of destination filesystem
    dest_dir = dest_parent_dir(dest_fs, src_dir)

    # compute key of the path of the source filesystem
    _, key = dest_fs.path2key(j.sal.fs.joinPaths(dest_fs.rootpath, src_dir.dbobj.location))
    if not dest_fs.dirCollection.exists(key):
        # the source dir doesn't exist yet in the destination filesystem
        dest_dirobj = dest_fs.dirCollection.new()
        copy = src_dir.dbobj.to_dict()
        copy.pop("contents")
        dest_dirobj.dbobj.from_dict(copy)
        dest_dirobj.key = key
        self._log_debug("copy directory :{} {}".format(src_dir.dbobj.location, src_dir.key))
        dest_dirobj.save()

        # add new inode in the current directory that poing to the newly
        # creation directory
        inode = ModelCapnp.Inode.new_message()
        inode.name = dest_dirobj.dbobj.name
        inode.size = dest_dirobj.dbobj.size
        inode.aclkey = dest_dirobj.dbobj.aclkey
        inode.creationTime = dest_dirobj.dbobj.creationTime
        inode.modificationTime = dest_dirobj.dbobj.modificationTime
        dir_type = inode.attributes.init("dir")
        dir_type.key = dest_dirobj.key

        dest_dir.addSubItem("contents", inode)
        dest_dir.reSerialize()
        dest_dir.save()

    # copy aci
    if not dest_fs.aciCollection.exists(dirobj.dbobj.aclkey):
        aci_dest = dest_fs.aciCollection.new()
        aci_src = src_fs.aciCollection.get(dirobj.dbobj.aclkey)
        aci_dest.dbobj.from_dict(aci_src.dbobj.to_dict())
        self._log_debug("copy aci :{}".format(aci_dest.key))
        aci_dest.save()

    return True


def fileFunction(dirobj, type, name, args, subobj):
    dest_fs = args["dest_fs"]
    src_fs = args["src_fs"]

    dest_dir = dest_current_dir(dest_fs, dirobj)
    dest_dir.fileReplace(subobj, create=True)

    # copy aci
    if not dest_fs.aciCollection.exists(subobj.aclkey):
        aci_dest = dest_fs.aciCollection.new()
        aci_src = src_fs.aciCollection.get(subobj.aclkey)
        aci_dest.dbobj.from_dict(aci_src.dbobj.to_dict())
        self._log_debug("copy aci :{}".format(aci_dest.key))
        aci_dest.save()


def linkFunction(dirobj, type, name, args, subobj):
    dest_fs = args["dest_fs"]
    src_fs = args["src_fs"]

    dest_dir = dest_current_dir(dest_fs, dirobj)
    if not dest_dir.linkExists(subobj.name):
        # add new file inode in the current directory
        dest_dir.addSubItem("contents", subobj)
        dest_dir.reSerialize()
        dest_dir.save()

    # copy aci
    if not dest_fs.aciCollection.exists(subobj.aclkey):
        aci_dest = dest_fs.aciCollection.new()
        aci_src = src_fs.aciCollection.get(subobj.aclkey)
        aci_dest.dbobj.from_dict(aci_src.dbobj.to_dict())
        self._log_debug("copy aci :{}".format(aci_dest.key))
        aci_dest.save()


def specialFunction(dirobj, type, name, args, subobj):
    dest_fs = args["dest_fs"]
    src_fs = args["src_fs"]

    dest_dir = dest_current_dir(dest_fs, dirobj)
    if not dest_dir.fileSpecialExists(subobj.name):
        # add new file inode in the current directory
        dest_dir.addSubItem("contents", subobj)
        dest_dir.reSerialize()
        dest_dir.save()

    # copy aci
    if not dest_fs.aciCollection.exists(subobj.aclkey):
        aci_dest = dest_fs.aciCollection.new()
        aci_src = src_fs.aciCollection.get(subobj.aclkey)
        aci_dest.dbobj.from_dict(aci_src.dbobj.to_dict())
        self._log_debug("copy aci :{}".format(aci_dest.key))
        aci_dest.save()


def main():
    kvs = j.data.kvs.getRocksDBStore(name="flist", namespace=None, dbpath="/tmp/jumpcale.db")
    fjs = j.tools.flist.getFlist(rootpath="/tmp/rootB", kvs=kvs)
    fjs.add("/tmp/rootB")

    kvs = j.data.kvs.getRocksDBStore(name="flist", namespace=None, dbpath="/tmp/ardb.db")
    fardb = j.tools.flist.getFlist(rootpath="/tmp/rootA", kvs=kvs)
    fardb.add("/tmp/rootA")

    kvs = j.data.kvs.getRocksDBStore(name="flist", namespace=None, dbpath="/tmp/merge.db")
    fdest = j.tools.flist.getFlist(rootpath="/", kvs=kvs)

    merger = FlistMerger()
    merger.add_source(fjs)
    merger.add_source(fardb)
    merger.add_destination(fdest)
    merger.merge()

    fdest.pprint()


if __name__ == "__main__":
    main()
