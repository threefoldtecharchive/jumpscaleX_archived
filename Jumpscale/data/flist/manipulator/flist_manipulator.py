"""
This module implement path manipulation on a Flist.
"""

from Jumpscale import j
import os
from .path import Path
import g8storclient
import tarfile
import base64


class FlistManipulatorFactory:
    def create(self, path):
        """
        create an empty flist and save it at `path`
        """
        if not os.path.isabs(path):
            raise j.exceptions.Input("path needs to be absolute")

        if os.path.exists(path):
            raise j.exceptions.Input("path %s already exists" % path)

        kvs = j.data.kvs.getRocksDBStore("flist", namespace=None, dbpath=path)
        flist = j.tools.flist.getFlist(rootpath="/", kvs=kvs)

        _, key = flist.path2key(flist.rootpath)
        if not flist.dirCollection.exists(key):
            root_dir = flist.dirCollection.new()
            root_dir.dbobj.creationTime = j.data.time.epoch
            root_dir.dbobj.creationTime = root_dir.dbobj.creationTime
            root_dir.dbobj.name = "/"
            root_dir.key = key
            root_dir.save()
        else:
            return self.get(path)

        root = Path(obj=root_dir.dbobj, parent=None, flist=flist)
        return Manipulator(root, kvs, path)

    def get(self, path):
        """
        load an existing flist from path
        """
        kvs = j.data.kvs.getRocksDBStore("flist", namespace=None, dbpath=path)
        flist = j.tools.flist.getFlist(rootpath="/", kvs=kvs)
        _, key = flist.path2key(flist.rootpath)
        root_dir = flist.dirCollection.get(key)

        root = Path(obj=root_dir.dbobj, parent=None, flist=flist)
        return Manipulator(root, kvs, path)


class Manipulator:
    def __init__(self, root, kvs, output_path):
        # keep a set of all the files added to the existing flist
        # so we can upload them to a backend after we're done manipulating the flist
        self.add_files = []
        self.root = root
        self._kvs = kvs
        self.output_path = output_path

    def __del__(self):
        self.close()

    def close(self):
        """
        properly close the rocksdb
        """
        self._kvs.close()

    def get_dir(self, location):
        """
        get a Path object on location
        """
        if not os.path.isabs(location):
            raise j.exceptions.Value("location must be an absolute path")
        if location:
            dir = self.root
            for dir in location.split(os.path.sep)[1:]:
                dir = dir.dirs(dir)[0]

        return dir

    def export(self):
        output = self.output_path + ".tgz"
        self._log_info("export the flist at %s", output)

        with tarfile.open(output, "w:gz") as tar:
            tar.add(self.output_path)

        return output

    def upload(self, backend, direct=False):
        """
        @param client: backend client. Can be a redis client or ardb client
            - example: j.clients.redis.get(ipaddr=<ipaddr>, port=<port>, ardb_patch=True))
        @param direct: bool, if True, will use the directhub client to upload the data
                        directhub client allow to test existence and upload per batch  key and data
                        If false, simple use exist/set from the backend client
        """
        self._kvs.close()

        for path in self.root._flist._added_files:
            if not os.path.exists(path):
                raise j.exceptions.Base("file not found %s" % path)

            self._log_debug("hash %s", path)
            hashs = g8storclient.encrypt(path)

            if hashs is None:
                return

            for hash in hashs:
                if not backend.exists(hash["hash"]):
                    self._log_debug("upload %s", path)
                    backend.set(hash["hash"], hash["data"])

        return self.export()

    def upload_diff(self, backend_instance):
        """
        @param backend_instance: instance name of the hubdirect client to use
        """
        directclient = j.clients.hubdirect.get(backend_instance, create=False, interactive=False)

        hash_data = {}
        to_upload = []

        for path in self.root._flist._added_files:
            data = g8storclient.encrypt(path) or []
            for item in data:
                hash_data[item["hash"]] = item["data"]
            # keys.extend([x['hash'] for x in data])

        res = directclient.exists(list(hash_data.keys()))
        missing_keys = res.json()
        missing_keys = list(map(base64.b64decode, missing_keys))
        missing_keys = list(map(bytes.decode, missing_keys))
        # let's adding all missing keys
        to_upload.extend(missing_keys)

        self._log_info("[+] %d chunks to upload" % len(to_upload))

        if len(to_upload) == 0:
            return

        # filter the has_data dict to only keep what needs to be uploaded
        upload = {k: v for k, v in hash_data.items() if k in to_upload}
        self._log_info("[+] uploading last data...")
        directclient.insert(upload)

        return self.export()
