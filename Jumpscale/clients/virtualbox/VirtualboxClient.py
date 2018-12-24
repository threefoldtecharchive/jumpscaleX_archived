from Jumpscale import j

JSBASE = j.application.JSBaseClass

from .VirtualboxVM import VirtualboxVM
from .VirtualboxDisk import VirtualboxDisk


class VirtualboxClient(j.application.JSBaseClass):
    """
    info
        https://github.com/SethMichaelLarson/virtualbox-python
    """

    def __init__(self):
        JSBASE.__init__(self)
        self._logger_enable()
        self.vms={}
        self.disks = {}

    def _cmd(self, cmd):
        cmd = "VBoxManage %s" % cmd
        self._logger.debug("vb cmd:%s" % cmd)
        rc, out, err = j.sal.process.execute(cmd)
        return out

    def vms_list(self):
        result = {}
        res = self._cmd("list vms")
        if res.strip() == "":
            return {}
        for l in res.split("\n"):
            if l.strip() is "":
                continue
            if "{" not in l:
                continue
            pre, post = l.split("{", 1)
            guid = post.split("}", 1)[0]
            name = pre.strip().strip("\"").strip()
            result[name.lower().strip()] = guid.strip()
        return result

    def vms_get(self):
        res = []
        for key, d in self.vms_list().items():
            res.append(self.vm_get(name=key))
        return res

    def _parse(self, txt, identifier="UUID:"):
        res = []
        for l in txt.split("\n"):
            if l.startswith(identifier):
                res.append({})
                last = res[-1]
            if ":" in l:
                pre, post = l.split(":", 1)
                name = pre.strip().strip("'").strip()
                last[name.lower().strip()] = post.strip().strip("'").strip()
        return res

    def vdisks_list(self):
        """
        :return: list of disk paths
        """
        out = self._cmd("list hdds -l")


        return self._parse(out, identifier="UUID:")

    def hostonlyifs_list(self):
        out = self._cmd("list hostonlyifs -l -s")
        return self._parse(out, identifier="Name:")

    def vdisks_get(self):
        res = []
        for disk in self.vdisks_list():
            res.append(self.disk_get(path=disk["location"]))
        return res

    def reset_all(self):
        for vm in self.vms_get():
            vm.stop()
            from time import sleep
            sleep(5)
            vm.delete()
        for disk in self.vdisks_get():
            disk.delete()

    def vm_get(self, name):
        if name not in self.vms:
            self.vms[name] = VirtualboxVM(name=name)
        return self.vms[name]

    def disk_get(self, path):
        if path not in self.disks:
            self.disks[path] = VirtualboxDisk(client=self, path=path)
        return self.disks[path]
