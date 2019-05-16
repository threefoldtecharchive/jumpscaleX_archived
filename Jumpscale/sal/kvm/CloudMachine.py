from Jumpscale import j
from sal.kvm.Machine import Machine


class CloudMachine(Machine):
    """
    Wrapper class around our machine object , to use with jumpscale libs.
    """

    def __init__(self, controller, name, os, disks, nics, memory, cpucount, poolname="vms", cloud_init=False):
        """
        Machine object instance.

        @param contrller object(j.sal.kvm.KVMController()): controller object to use.
        @param name str: machine name.
        @param os str: os name to use.
        @param disks list of int: size of disk names to be used by the machine.
                                  first of the list is the size of the boot disk, remaining are data disks
        @param nics [str]: name of networks to be used with machine.
        @param memory int: disk memory in Mb.
        @param cpucount int: number of cpus to use.
        @param cloud_init bool: option to use cloud_init passing creating and passing ssh_keys, user name and passwd to
        the image
        """
        self.pool = j.sal.kvm.Pool(controller, poolname)
        self.os = os
        new_nics = list(
            map(lambda x: j.sal.kvm.Interface(controller, j.sal.kvm.Network(controller, x, x, []), x), nics)
        )
        if disks:
            new_disks = [j.sal.kvm.Disk(controller, self.pool, "%s-base.qcow2" % name, disks[0], os)]
            for i, disk in enumerate(disks[1:]):
                new_disks.append(j.sal.kvm.Disk(controller, self.pool, "%s-data-%s.qcow2" % (name, i), disk))
        else:
            new_disks = []

        super().__init__(controller, name, new_disks, new_nics, memory, cpucount, cloud_init=cloud_init)

    @classmethod
    def from_xml(cls, controller, xml):
        """
        Instantiate a cloud Machine object using the provided xml source and kvm controller object.

        @param controller object(j.sal.kvm.KVMController): controller object to use.
        @param source  str: xml string of machine to be created.
        """
        # TODO fix
        m = Machine.from_xml(controller, xml)
        return cls(
            m.controller,
            m.name,
            m.disks and m.disks[0].image_name,
            list(map(lambda disk: disk.size, m.disks)),
            list(map(lambda nic: nic.name, m.nics)),
            m.memory,
            m.cpucount,
            m.disks and m.disks[0].pool.name,
            cloud_init=m.cloud_init,
        )

    def create(self, username="root", passwd="gig1234", sshkey=None):
        """
        Create and define the instanse of the machine xml onto libvirt.

        @param username  str: set the username to be set in the machine on boot.
        @param passwd str: set the passwd to be set in the machine on boot.
        @param sshkey str: public sshkey to authorize in the vm
        """
        if self.is_created:
            return False
        else:
            [disk.create() for disk in self.disks if not disk.is_created]
            return super().create(username=username, passwd=passwd, sshkey=sshkey)

    def start(self):
        """
        Start machine.
        """
        return super().start() if not self.is_started else False

    def delete(self):
        """
        Undefine machine from libvirt.
        """
        return super().delete() if self.is_created else False

    def shutdown(self, force=False):
        """
        Shutdown machine.
        """
        return super().shutdown(force) if self.is_started else False

    stop = shutdown

    def suspend(self):
        """
        Suspend machine, similar to hibernate.
        """
        return super().suspend() if self.is_started else False

    pause = suspend

    def resume(self):
        """
        Resume machine if suspended.
        """
        return super().resume() if self.state == "paused" else False
