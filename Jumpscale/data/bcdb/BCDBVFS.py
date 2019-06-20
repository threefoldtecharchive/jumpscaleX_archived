from Jumpscale import j


class BCDBVFS:
    def __init__(self):
        self._dirs_cache={}
        self.serializer = j.data.serializers.json


    def _dir_get(self,path):
        splitted = path.split("/"):
        sid=None
        hash=None
        url=None
        if path.startswith("/data"):
            if "url" in splitted:
                url = splitted[-1]
                key="data_%s_%s"%(nid,url)
            elif "url" in splitted:
                j.shell()
            elif "hash" in splitted:
                j.shell()
            nid = splitted[1]

        if not key in self._dirs_cache:
             self._dirs_cache[key]=BCDBVFS_Dir_Data(self,path,nid=nid, url=url)
        return self._dirs_cache[key]

    def list(self, path):
        d=self._dir_get(path)
        bname = j.sal.fs.getBasename(path)
        return d.list(bname)

        pass

    def get(self, path):
        d=self._dir_get(path)
        bname = j.sal.fs.getBasename(path)
        res = d.get(bname)
        res2= self.serializer.dumps(res)
        return res2

    def set(self, path):
        pass

    def delete(self, path):
        pass

    def len(self):
        return 1

class BCDBVFS_Dir_Data:
    def __init__(self,vfs,nid,url=None,sid=None,hash=None):
        self.vfs = vfs
        self.nid=nid
        if url:
            pass
        j.shell()
        self.model

    def list(self):
        pass

    def get(self):
        pass

    def set(self):
        pass

    def len(self):
        pass
