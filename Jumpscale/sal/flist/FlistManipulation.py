from Jumpscale import j


class FlistManipulation(j.application.JSBaseClass):
    """
    this sal using zflist bin should install using `j.builders.storage.zflist.install(reset=True)`
    """

    __jslocation__ = "j.sal.flist"

    def __init__(self):
        self.hub = {"host": "playground.hub.grid.tf", "port": 9910}

    @classmethod
    def _zflist(cls, path, hub, *args):
        j.sal.process.setEnvironmentVariable(
            ["ZFLIST_BACKEND", "ZFLIST_MNT", "ZFLIST_JSON"], [j.data.serializers.json.dumps(hub), path, "1"]
        )

        _, out, _ = j.sal.process.execute("zflist " + " ".join(args), showout=False)

        if "cat" in args:
            out = out.split("[+]")
            return out[-2]

        out = out.split("\n")
        for response in out:
            if "success" in response:
                return j.data.serializers.json.loads(response)

    def new(self):
        """
        initialize an empty flist to enable editing
        """
        tmp = j.sal.fs.getTmpDirPath()
        self._zflist(tmp, self.hub, "init")

        return Flist(tmp, self.hub)

    def open(self, flist):
        """
        open an flist to enable editing
        """

        tmp = j.sal.fs.getTmpDirPath()
        self._zflist(tmp, self.hub, "open", flist)
        return Flist(tmp, self.hub)


class Flist(object):
    def __init__(self, path, hub):
        self.__path = path
        self.__hub = hub

    def __del__(self):
        self.close()

    @property
    def path(self):
        return self.__path

    @property
    def hub(self):
        return self.__hub

    def _zflist(self, *args):
        return FlistManipulation._zflist(self.path, self.hub, *args)

    def put(self, src, dest):
        """
        insert local file into the flist
        """
        return self._zflist("put", src, dest)["success"]

    def put_dir(self, src, dest):
        """
        insert local directory into the flist (recursively)
        """
        return self._zflist("putdir", src, dest)["success"]

    def remove_file(self, path):
        """
        remove a file (not a directory)
        """
        return self._zflist("rm", path)["success"]

    def remove_dir(self, path):
        """
        remove a directory (recursively)
        """
        return self._zflist("rmdir", path)["success"]

    def create_dir(self, path):
        """
        create an empty directory (non-recursive)
        """
        return self._zflist("mkdir", path)["success"]

    def merge(self, flist_path):
        """
        merge another flist into the current one
        """
        return self._zflist("merge", path)["success"]

    def chmod(self, mode, file):
        """
        change mode of a file (like chmod command)
        chmod [reference][operator][mode] file... 
        """
        return self._zflist("chmod", mode, file)["success"]

    def list(self, path="/"):
        """
       list the content of a directory in flist
        """
        return self._zflist("ls", path)["response"]

    def list_all(self):
        """
       list full contents of files and directories
        """
        return self._zflist("find")["response"]

    def set_metadata(self, hub_host="playground.hub.grid.tf", port=9910):
        """
       set metadata
        """
        return self._zflist("metadata backend", "--host {}".format(hub_host), "--port {}".format(port))["success"]

    def print_content(self, path):
        """
        print file contents (backend metadata required)
        """
        self.set_metadata()
        print(self._zflist("cat", path))

    def commit(self, path):
        """
        commit changes to a new flist
        """
        self.set_metadata()
        return self._zflist("commit", path)["success"]

    def close(self):
        """
        close mountpoint and discard files
        """
        self.set_metadata()
        self._zflist("close")
        j.sal.fs.remove(self.path)
        return True

