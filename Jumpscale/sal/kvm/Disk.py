from Jumpscale import j
import libvirt
from xml.etree import ElementTree
from sal.kvm.BaseKVMComponent import BaseKVMComponent
from sal.kvm.StorageController import StorageController


class Disk(BaseKVMComponent):
    """
    Wrapper class around libvirt's storage volume object , to use with jumpscale libs.
    """

    def __init__(self, controller, pool, name, size, image_name="", disk_iops=None):
        """
        Disk object instance.

        @param controller object(j.sal.kvm.KVMController()): controller object to use.
        @param pool str: name of the pool to add disk to.
        @param name str: name of the disk.
        @param size int: size of disk in Gb.
        @param image_name  str: name of image to load on disk  if available.
        @param disk_iops int: total throughput limit in bytes per second.
        """
        BaseKVMComponent.__init__(controller=controller)
        self.size = size
        self.image_name = image_name
        self.controller = controller
        self.pool = pool
        self.name = name
        self.disk_iops = int(disk_iops) if disk_iops else None
        self._volume = None

    @staticmethod
    def get_volume(disk_name, pool):
        """
        Return libvirt's storage volume instance with disk_name if created.

        @param disk_name str: disk name to search for.
        @param pool: object(j.sal.kvm.Pool) pool in which the disk belongs
        """
        try:
            volume = pool.storageVolLookupByName(disk_name)
            return volume
        except BaseException:
            return None

    @property
    def volume(self):
        """
        Return libvirt's storage volume instance with disk_name if created.
        """
        if self._volume is None:
            self._volume = self.pool.storageVolLookupByName(self.name)
        return self._volume

    @property
    def is_created(self):
        """
        Check if the disk is created (defined) in libvirt
        """
        try:
            self.pool.lvpool.storageVolLookupByName(self.name)
            return True
        except libvirt.libvirtError as e:
            # return false if volume is not found
            if e.get_error_code() == libvirt.VIR_ERR_NO_STORAGE_VOL:
                return False
            # raise if any other error
            raise e

    @property
    def is_started(self):
        return self.volume.isActive() == 1

    def create(self):
        """
        Create the actual volume in libvirt
        """
        volume = self.pool.lvpool.createXML(self.to_xml(), 0)
        # return libvirt volume obj
        return volume

    def start(self):
        return NotImplementedError()

    def delete(self):
        """
        Delete the disk
        """
        if not self.is_created:
            return

        self.volume.wipe(0)
        self.volume.delete(0)
        return True

    def stop(self):
        return NotImplementedError()

    def to_xml(self):
        """
        Export disk object to xml
        """

        disktemplate = self.controller.get_template("disk.xml")
        if self.image_name:
            diskbasevolume = self.controller.executor.prefab.core.joinpaths(
                self.controller.base_path, "images", "%s" % self.image_name
            )
        else:
            diskbasevolume = ""
        diskpath = self.controller.executor.prefab.core.joinpaths(self.pool.poolpath, "%s.qcow2" % self.name)
        diskxml = disktemplate.render(
            {"diskname": self.name, "diskpath": diskpath, "disksize": self.size, "diskbasevolume": diskbasevolume}
        )
        return diskxml

    @classmethod
    def from_xml(cls, controller, diskxml):
        """
        Create Disk object from xml.

        @controller object(j.sal.kvm.KVMController()): controller object to use.
        @diskxml str: xml representation of the disk
        """

        disk = ElementTree.fromstring(diskxml)
        name = disk.findtext("name")
        pool_name = disk.find("source").get("pool")
        pool = StorageController(controller).get_pool(pool_name)
        size = disk.findtext("capacity")
        if disk.find("backingStore") is not None and disk.find("backingStore").find("source") is not None:
            path = disk.find("backingStore").find("source").get("file")
            image_name = path.split("/")[-1].split(".")[0]
        else:
            image_name = ""
        return cls(controller, pool, name, size, image_name)

    @classmethod
    def get_by_name(cls, controller, name):
        raise j.exceptions.NotImplemented()

    def clone_disk(self, new_disk):
        """
        Clone the disk
        @param new_disk: object(j.sal.kvm.Disk). new disk object
        """
        cloned_volume = self.pool.createXMLFrom(new_disk.to_xml(), self.volume, 0)
        return cloned_volume
