from Jumpscale import j
from stat import *
import brotli
import subprocess
import os
import tempfile
import shutil
import re

import capnp
from . import model_capnp as ModelCapnp

from .FList import FList
from .FListMetadata import FListMetadata
from .FlistMerger import FlistMerger
from .manipulator.flist_manipulator import FlistManipulatorFactory

from .models import DirModel
from .models import DirCollection
from .models import ACIModel
from .models import ACICollection

# from .FuseExample import FuseExample # test also disabled (see below)


class FListFactory:
    def __init__(self):
        self.__jslocation__ = "j.tools.flist"
        self.__imports__ = "brotli,pycapnp"
        self.manipulator = FlistManipulatorFactory()

    def getCapnpSchema(self):
        return ModelCapnp

    def getDirCollectionFromDB(self, name="test", kvs=None):
        """
        std keyvalue stor is redis used by core
        use a name for each flist because can be cached & stored in right key value stor
        """
        schema = self.getCapnpSchema()

        # now default is mem, if we want redis as default store uncomment next,
        # but leave for now, think mem here ok
        if kvs is None:
            kvs = j.data.kvs.getRedisStore(name="flist", namespace=name, unixsocket="%s/redis.sock" % j.dirs.TMPDIR)

        collection = j.data.capnp.getModelCollection(
            schema.Dir,
            category="flist_%s" % name,
            modelBaseClass=DirModel,
            modelBaseCollectionClass=DirCollection,
            db=kvs,
            indexDb=kvs,
        )
        return collection

    def getACICollectionFromDB(self, name="test", kvs=None):
        """
        if kvs None then mem will be used

        """
        schema = self.getCapnpSchema()

        if kvs is None:
            kvs = j.data.kvs.getRedisStore(name="flist", namespace=name, unixsocket="%s/redis.sock" % j.dirs.TMPDIR)

        collection = j.data.capnp.getModelCollection(
            schema.ACI,
            category="ACI_%s" % name,
            modelBaseClass=ACIModel.ACIModel,
            modelBaseCollectionClass=ACICollection.ACICollection,
            db=kvs,
            indexDb=kvs,
        )
        return collection

    def getUserGroupCollectionFromDB(self, name="usergroup", kvs=None):
        """
        if kvs None then mem will be used
        """
        schema = self.getCapnpSchema()

        if kvs is None:
            kvs = j.data.kvs.getRedisStore(name="flist", namespace=name, unixsocket="%s/redis.sock" % j.dirs.TMPDIR)

        collection = j.data.capnp.getModelCollection(
            schema.UserGroup,
            category="ug_%s" % name,
            modelBaseClass=ACIModel.ACIModel,
            modelBaseCollectionClass=ACICollection.ACICollection,
            db=kvs,
            indexDb=kvs,
        )
        return collection

    def getFlist(self, rootpath="/", namespace="", kvs=None):
        """
        @param namespace, this normally is some name you cannot guess, important otherwise no security
        Return a Flist object
        """
        dirCollection = self.getDirCollectionFromDB(name="%s:dir" % namespace, kvs=kvs)
        aciCollection = self.getACICollectionFromDB(name="%s:aci" % namespace, kvs=kvs)
        userGroupCollection = self.getUserGroupCollectionFromDB(name="%s:users" % namespace, kvs=kvs)
        return FList(
            rootpath=rootpath,
            namespace=namespace,
            dirCollection=dirCollection,
            aciCollection=aciCollection,
            userGroupCollection=userGroupCollection,
        )

    def getFlistMetadata(self, rootpath="/", namespace="main", kvs=None):
        """
        @param namespace, this normally is some name you cannot guess, important otherwise no security
        Return a FlistMetadata object
        """
        flist = self.getFlist(rootpath=rootpath, namespace=namespace, kvs=kvs)
        return FListMetadata(flist)

    def get_archiver(self):
        """
        Return a FListArchiver object

        This is used to push flist to IPFS
        """
        return FListArchiver()

    def get_merger(self):
        return FlistMerger()

    def test_fuse(self):
        """ DISABLED as FuseExample has been commented out
        """
        return
        TEST_DIR = tempfile.mkdtemp()  # use a temporary directory...
        FuseExample(TEST_DIR)
        shutil.rmtree(TEST_DIR)  # ... and delete it afterwards

    def test(self):

        testDir = tempfile.mkdtemp()  # use a temporary directory...
        flist = self.getFlist(rootpath=testDir)
        flist.add(testDir)

        def pprint(path, ddir, name):
            self._log_debug(path)

        flist.walk(fileFunction=pprint, dirFunction=pprint, specialFunction=pprint, linkFunction=pprint)

        shutil.rmtree(testDir)  # ... and delete it afterwards

    def destroy(self, rootpath="/", namespace="main", kvs=None):
        fl = self.getFlist(rootpath, namespace, kvs)
        fl.destroy()


class FListArchiver:
    # This is a not efficient way, the only other possibility
    # is to call brotli binary to compress big file if needed
    # currently, this in-memory way is used

    def __init__(self, ipfs_cfgdir=None):
        cl = j.tools.prefab.local
        self._ipfs = cl.core.command_location("ipfs")
        if not ipfs_cfgdir:
            self._env = "IPFS_PATH=%s" % cl.core.replace("{DIR_BASE}/cfg/ipfs/main")
        else:
            self._env = "IPFS_PATH=%s" % ipfs_cfgdir

    def _compress(self, source, destination):
        with open(source, "rb") as content_file:
            content = content_file.read()

        compressed = brotli.compress(content, quality=6)

        with open(destination, "wb") as output:
            output.write(compressed)

    # def push_to_ipfs(self, source):
    #     cmd = "%s %s add '%s'" % (self._env, self._ipfs, source)
    #     out = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

    #     m = re.match(r'^added (.+) (.+)$', out.stdout.decode())
    #     if m is None:
    #         raise j.exceptions.Base('invalid output from ipfs add: %s' % out)

    #     return m.group(1)

    def build(self, flist, backend):
        hashes = flist.getHashList()

        if not os.path.exists(backend):
            os.makedirs(backend)

        for hash in hashes:
            files = flist.filesFromHash(hash)

            # skipping non regular files
            if not flist.isRegular(files[0]):
                continue

                self._log_debug("Processing: %s" % hash)

            root = "%s/%s/%s" % (backend, hash[0:2], hash[2:4])
            file = hash

            target = "%s/%s" % (root, file)

            if not os.path.exists(root):
                os.makedirs(root)

            # compressing the file
            self._compress(files[0], target)

            # adding it to ipfs network
            hash = self.push_to_ipfs(target)
            self._log_debug("Network hash: %s" % hash)

            # updating flist hash with ipfs hash
            for f in files:
                flist.setHash(f, hash)

        self._log_debug("Files compressed and shared")
