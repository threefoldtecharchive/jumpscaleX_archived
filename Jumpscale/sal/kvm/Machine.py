from xml.etree import ElementTree
from Jumpscale import j
import libvirt
import yaml
from sal.kvm.BaseKVMComponent import BaseKVMComponent
from sal.kvm.MachineSnapshot import MachineSnapshot
from time import sleep


class Machine(BaseKVMComponent):
    """
    Wrapper class around libvirt's machine object , to use with jumpscale libs.
    """

    STATES = {
        0: "nostate",
        1: "running",
        2: "blocked",
        3: "paused",
        4: "shutdown",
        5: "shutoff",
        6: "crashed",
        7: "pmsuspended",
        8: "last",
    }

    def __init__(self, controller, name, disks, nics, memory, cpucount, cloud_init=False):
        """
        Machine object instance.

        @param contrller object(j.sal.kvm.KVMController()): controller object to use.
        @param name str: machine name
        @param disks [object(j.sal.kvm.Disk())]: list of disk instances to be used with machine.
        @param nics [object(j.sal.kvm.interface())]: instance of networks to be used with machine.
        @param memory int: disk memory in Mb.
        @param cpucount int: number of cpus to use.
        @param cloud_init bool: option to use cloud_init passing creating and passing ssh_keys,
         user name and passwd to the image
        """
        BaseKVMComponent.__init__(controller=controller)
        self.name = name
        self.disks = disks
        self.nics = nics
        self.memory = memory
        self.cpucount = cpucount
        self.controller = controller
        self.cloud_init = cloud_init
        self.image_path = "%s/%s_ci.iso" % (self.controller.base_path, self.name) if cloud_init else ""
        self._domain = None
        self._ip = None
        self._executor = None

    @property
    def is_created(self):
        """
        Return bool option is machine defined in libvirt or not.
        """
        try:
            self.domain
            return True
        except libvirt.libvirtError as e:
            return False

    @property
    def is_started(self):
        """
        Check if machine is started.
        """
        return bool(self.domain.isActive())

    def create(self, username="root", passwd="gig1234", sshkey=None):
        """
        Create and define the instanse of the machine xml onto libvirt.

        @param username  str: set the username to be set in the machine on boot.
        @param passwd str: set the passwd to be set in the machine on boot.
        @param sshkey str: public sshkey to authorize in the vm
        """
        prefab = self.controller.executor.prefab
        prefab.core.dir_ensure("%s/metadata/%s" % (self.controller.base_path, self.name))
        if self.cloud_init:

            sshkeys_to_authorize = [self.controller.pubkey]
            if sshkey:
                sshkeys_to_authorize.append(sshkey)

            prefab.core.dir_ensure("%s/metadata/%s" % (self.controller.base_path, self.name))
            userdata = "#cloud-config\n"
            userdata += yaml.dump(
                {
                    "chpasswd": {"expire": False},
                    "ssh_pwauth": True,
                    "users": [
                        {
                            "lock-passwd": False,
                            "name": username,
                            "plain_text_passwd": passwd,
                            "shell": "/bin/bash",
                            "ssh-authorized-keys": sshkeys_to_authorize,
                            "sudo": "ALL=(ALL) NOPASSWD: ALL",
                        }
                    ],
                }
            )
            metadata = '{"local-hostname":"vm-%s"}' % self.name
            userdata_path = "%s/metadata/%s/user-data" % (self.controller.base_path, self.name)
            metadata_path = "%s/metadata/%s/meta-data" % (self.controller.base_path, self.name)
            prefab.core.file_write(userdata_path, userdata)
            prefab.core.file_write(metadata_path, metadata)
            cmd = "genisoimage -o {base}/{name}_ci.iso -V cidata -r -J {metadata_path} {userdata_path}".format(
                base=self.controller.base_path, name=self.name, metadata_path=metadata_path, userdata_path=userdata_path
            )
            prefab.core.run(cmd)
            prefab.core.dir_remove("%s/images/%s " % (self.controller.base_path, self.name))
        self.domain = self.controller.connection.defineXML(self.to_xml())

    def start(self):
        """
        Start machine.
        """
        if self.is_started:
            return 0
        return self.domain.create() == 0

    def delete(self):
        """
        Undefine machine in libvirt.
        """
        if not self.is_created:
            return 0
        return self.domain.undefine() == 0

    def to_xml(self):
        """
        Return libvirt's xml string representation of the machine.
        """
        machinexml = self.controller.get_template("machine.xml").render(
            {
                "machinename": self.name,
                "memory": self.memory,
                "nrcpu": self.cpucount,
                "nics": self.nics,
                "disks": self.disks,
                "cloudinit": self.cloud_init,
                "image_path": self.image_path,
            }
        )
        return machinexml

    @classmethod
    def from_xml(cls, controller, source):
        """
        Instantiate a Machine object using the provided xml source and kvm controller object.

        @param controller object(j.sal.kvm.KVMController): controller object to use.
        @param source  str: xml string of machine to be created.
        """
        machine = ElementTree.fromstring(source)
        name = machine.findtext("name")
        memory = int(machine.findtext("memory"))
        nrcpu = int(machine.findtext("vcpu"))
        interfaces = list(
            map(
                lambda interface: j.sal.kvm.Interface.from_xml(controller, ElementTree.tostring(interface)),
                machine.find("devices").findall("interface"),
            )
        )
        xml_disks = [disk for disk in machine.find("devices").findall("disk") if disk.get("device") == "disk"]
        disks = list(map(lambda disk: j.sal.kvm.Disk.from_xml(controller, ElementTree.tostring(disk)), xml_disks))
        cloud_init = bool([disk for disk in machine.find("devices").findall("disk") if disk.get("device") == "cdrom"])
        return cls(controller, name, disks, interfaces, memory, nrcpu, cloud_init=cloud_init)

    @classmethod
    def get_by_name(cls, controller, name):
        """
        Get machine by name passing the controller to search with.
        """
        domain = controller.connection.lookupByName(name)
        return cls.from_xml(controller, domain.XMLDesc())

    @property
    def domain(self):
        """
        Returns the Libvirt Object of the current machines ,
        will be available if machine has been created at some point.
        """
        if not self._domain:
            self._domain = self.controller.connection.lookupByName(self.name)
        return self._domain

    @domain.setter
    def domain(self, val):
        self._domain = val

    @property
    def uuid(self):
        """
        Returns the uuid of this instance of the machine.
        """
        if not self._uuid:
            self._uuid = self.domain.UUIDString()
        return self._uuid

    @property
    def ip(self):
        """
        Retrun IP of this instance of the machine if started.
        """
        tries = 7
        if not self._ip:
            for i in range(tries):
                for nic in self.nics:
                    ip = nic.ip
                    if ip:
                        self._ip = ip
                        return ip
                if i != tries - 1:
                    sleep(5)
        return self._ip

    @property
    def executor(self):
        """
        Return Executor obj where the conrtoller is connected.
        """
        port = 22
        if self.cloud_init and not self._executor:
            for i in range(5):
                rc = self.controller.executor.prefab.core.run("echo | nc %s %s" % (self.ip, port))[0]
                if rc == 0:
                    break
                sleep(5)
            self._executor = self.controller.executor.jumpto(
                addr=self.ip, login="cloudscalers", port=port, identityfile="/root/.ssh/libvirt"
            )
        return self._executor

    @property
    def prefab(self):
        """
        Return prefab object connected to this instance of the machine.
        """
        return self.executor.prefab

    @property
    def state(self):
        """
        Return the state if this instance of the machine which can be :

        0: nostate
        1: running
        2: blocked
        3: paused
        4: shutdown
        5: shutoff
        6: crashed
        7: pmsuspended
        8: last
        """
        return self.STATES[self.domain.state()[0]]

    def shutdown(self, force=False):
        """
        Shutdown machine.
        """
        if force:
            return self.domain.destroy() == 0
        else:
            return self.domain.shutdown() == 0

    # to fullfill the BaseKVMComponent iterface
    stop = shutdown

    def suspend(self):
        """
        Suspend machine, similar to hibernate.
        """
        return self.domain.suspend() == 0

    pause = suspend

    def resume(self):
        """
        Resume machine if suspended.
        """
        return self.domain.resume() == 0

    def create_snapshot(self, name, description=""):
        """
        Create snapshot of the machine, both disk and ram when reverted will continue as if suspended on this state.

        @param name str:   name of the snapshot.
        @param descrition str: descitption of the snapshot.
        """
        snap = MachineSnapshot(self.controller, self.domain, name, description)
        return snap.create()

    def load_snapshot(self, name):
        """
        Revert to snapshot name.

        @param name str: name of the snapshot to revvert to.
        """
        snap = self.domain.snapshotLookupByName(name)
        return self.domain.revertToSnapshot(snap)

    def list_snapshots(self, libvirt=False):
        """
        List snapshots of the current machine, if libvirt is true libvirt objects will be returned
        else the sal wrapper will be returned.

        @param libvirt bool: option to return libvirt snapshot obj or the sal wrapper.
        """
        snapshots = []
        snaps = self.domain.listAllSnapshots()
        if libvirt:
            return snaps
        for snap in snaps:
            snapshots.append(MachineSnapshot(self.controller, self, snap.getName()))
        return snapshots
