from Jumpscale import j


JSBASE = j.application.JSBaseClass


class VirtualboxDisk(j.application.JSBaseClass):
    def __init__(self, client, path):
        JSBASE.__init__(self)
        self.client = client
        self.path = path
        self._data = None

    def _cmd(self, cmd):
        cmd = "VBoxManage %s" % cmd
        self._logger.debug("vb cmd:%s" % cmd)
        rc, out, err = j.sal.process.execute(cmd)
        return out

    def create(self, reset=True, size=10000):
        if reset:
            self.delete()
        cmd = "createhd --filename '%s' --size %s" % (self.path, size)
        self._cmd(cmd)

    @property
    def size(self):
        c = self.data["capacity"]
        if "MByte" in c:
            cap = c.split(" ", 1)[0]
            return int(cap)
        else:
            raise RuntimeError("not implemented")

    @property
    def state(self):
        return self.data["state"].lower()

    @property
    def data(self):
        if not self._data:
            for item in self.client.vdisks_list():
                if item["location"] == self.path:
                    self._data = item
                    return self._data
            return None
        return self._data

    @property
    def uid(self):
        if self.data is None:
            return ""
        else:
            return self.data["UUID"]                

    @property
    def vm_name(self):
        """
        vm attached to this disk
        """
        if self.data==None:
            return None
        c = self.data["in use by vms"]
        if "UUID:" in c:
            name, post = c.split("(", 1)
            name = name.lower().strip()
            # uid = c.split("UUID:")[1].split(")")[0].strip()
            return name
        else:
            return None

    def delete(self):
        if self.data == None:
            return
        if self.vm is None:
            self._cmd("closemedium disk %s --delete" % self.uid)
        else:
            raise RuntimeError(
                "cannot delete disk because still attached to vm:%s" % self)

    def __repr__(self):
        return "vdisk:%s" % self.path

    __str__ = __repr__
