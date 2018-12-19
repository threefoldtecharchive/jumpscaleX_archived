from Jumpscale import j
import os

JSBASE = j.application.JSBaseClass
from .VirtualboxDisk import VirtualboxDisk



class VirtualboxVM(JSBASE):
    def __init__(self, name):
        JSBASE.__init__(self)
        self.client = j.clients.virtualbox.client
        self.name = name
        self._guid = ""
        self._logger_enable()

    def _cmd(self, cmd):
        cmd = "VBoxManage %s" % cmd
        self._logger.debug("vb cmd:%s" % cmd)
        rc, out, err = j.sal.process.execute(cmd,showout=False)
        return out

    def _cmd2(self, cmd):
        cmd = "VBoxManage modifyvm %s %s" % (self.name, cmd)
        self._logger.debug("vb2 cmd:%s" % cmd)
        rc, out, err = j.sal.process.execute(cmd,showout=False)
        return out

    def delete(self):
        if self.exists is False:
            return
        if self.is_running:
            self.stop()
            from time import sleep
            sleep(5)
        while self.name in self.client.vms_list():
            self._cmd("unregistervm %s --delete" % self.name)
        p = "%s/%s.vbox" % (self.path, self.name)
        if j.sal.fs.exists(p):
            j.sal.fs.remove(p)
        p = "%s/%s.vbox-prev" % (self.path, self.name)
        if j.sal.fs.exists(p):
            j.sal.fs.remove(p)
        self._logger.debug("delete done")

    @property
    def exists(self):
        cmd = "VBoxManage list vms"
        rc,out,err = j.sal.process.execute(cmd,showout=False)
        return self.name in out

    @property
    def path(self):
        return "%s/VirtualBox VMs/%s/" % (j.dirs.HOMEDIR, self.name)

    @property
    def guid(self):
        print("guid")
        from IPython import embed;
        embed(colors='Linux')

    @property
    def disks(self):
        res = []
        for item in self.client.vdisks_get():
            if item.vm_name == self.name:
                res.append(item.vm)
        return res

    def disk_create(self, name="main", size=10000, reset=True):
        path = "%s/%s.vdi" % (self.path, name)
        d = self.client.disk_get(path=path)
        d.create(size=size, reset=reset)
        self._logger.debug("disk create done")
        return d


    def hostnet(self, interface="vboxnet0"):
        # VBoxManage hostonlyif create
        if not j.sal.nettools.isNicConnected(interface):
        # rc, out, err = j.sal.process.execute("ip l sh dev %s" % interface)
        # if rc > 0:
            self._cmd("hostonlyif create")

    def create(self, reset=True, isopath="", datadisksize=10000, memory=2000, redis_port=4444):
        if reset:
            self.delete()

        self.hostnet("vboxnet0")

        cmd = "createvm --name %s  --ostype \"Linux_64\" --register" % (self.name)
        self._cmd(cmd)
        self._cmd2("--memory=%s " % (memory))
        self._cmd2("--ioapic on")
        self._cmd2("--boot1 dvd --boot2 disk")
        self._cmd2("--nic1 nat")
        self._cmd2("--nic2 hostonly")
        self._cmd2("--hostonlyadapter2 vboxnet0")
        self._cmd2("--vrde on")
        if redis_port:
            self._cmd2('--natpf1 "redis,tcp,,%s,,6379"' % redis_port)

        if datadisksize > 0:
            disk = self.disk_create(size=datadisksize, reset=reset)
            cmd = "storagectl %s --name \"SATA Controller\" --add sata  --controller IntelAHCI" % self.name
            self._cmd(cmd)
            cmd = "storageattach %s --storagectl \"SATA Controller\" --port 0 --device 0 --type hdd --medium '%s'" % (
            self.name, disk.path)
            self._cmd(cmd)

        if isopath:
            cmd = "storagectl %s --name \"IDE Controller\" --add ide" % self.name
            self._cmd(cmd)
            cmd = "storageattach %s --storagectl \"IDE Controller\" --port 0 --device 0 --type dvddrive --medium %s" % (
            self.name, isopath)
            self._cmd(cmd)
        self._logger.debug("create done")

    def start(self):
        args = ""
        if self.is_running:
            return
        # if running linux and environment
        # variable DISPLAY not set, we are probably
        # on a headless server (no X running), let's run
        # the virtual machine in background
        if j.core.platformtype.myplatform.isLinux:
            if not "DISPLAY" in os.environ:
                args += "--type headless"

        self._cmd('startvm %s "%s"' % (args, self.name))
        self._logger.debug("start done")

    @property
    def info(self):
        if not self.exists:
            return {}
        out = self._cmd("showvminfo %s"%self.name)
        tocheck={}
        tocheck["memory size"]="mem"
        tocheck["Number of CPUs"] = "nr_cpu"
        tocheck["State"] = "state"
        res={}
        for line in out.split("\n"):
            if line.strip()=="":
                continue
            line2=line.lower().strip()
            for key,alias in tocheck.items():
                if line.startswith(key):
                    res[alias]=line2.split(":",1)[1].strip()
        if "running" in res["state"]:
            res["state"]="running"
        else:
            res["state"] = "down"
        res["nr_cpu"]=int(res["nr_cpu"])
        return res

    @property
    def is_running(self):
        if "state" not in self.info:
            return False
        return self.info["state"]=="running"

    def stop(self):
        if self.is_running:
            try:
                self._cmd('controlvm "%s" poweroff' % self.name)
                self._logger.info("stopping vm : %s", self.name)
            except Exception as e:
                self._logger.info("vm : %s wasn't running" % self.name)
            self._logger.debug("stop done")

    def __repr__(self):
        return "vm: %-20s%s" % (self.name, self.path)

    __str__ = __repr__
