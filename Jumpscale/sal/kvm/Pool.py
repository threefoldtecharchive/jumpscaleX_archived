from Jumpscale import j
import libvirt
from xml.etree import ElementTree
from sal.kvm.BaseKVMComponent import BaseKVMComponent
from sal.kvm.Disk import Disk


class Pool(BaseKVMComponent):
    def __init__(self, controller, name):
        BaseKVMComponent.__init__(controller=controller)
        self.controller = controller
        self.name = name
        self.poolpath = self.controller.executor.prefab.core.joinpaths(self.controller.base_path, self.name)
        self._lvpool = None

    @property
    def is_created(self):
        try:
            self.controller.connection.storagePoolLookupByName(self.name)
            return True
        except libvirt.libvirtError as e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_STORAGE_POOL:
                return False
            raise e

    @property
    def is_started(self):
        return self.lvpool.isActive() == 1

    def create(self, start=True):
        """
        Create the bool
        """

        self.controller.executor.prefab.core.dir_ensure(self.poolpath)
        cmd = "chattr +C %s " % self.poolpath
        self.controller.executor.execute(cmd)
        self.controller.connection.storagePoolCreateXML(self.to_xml(), 0)

        if start:
            self.start()

    def start(self):
        """
        start a (previously defined) inactive pool
        """
        if self.is_started:
            return
        self.lvpool.create()

    def delete(self):
        """
        delete a pool
        destroy all volume in the pool before deleting the pool
        """
        for volume in self.lvpool.listAllVolumes():
            volume.wipe(0)
            volume.delete(0)

        self.lvpool.destroy()
        # seems destroy is enough
        # self.lvpool.delete()

    def stop(self):
        """
        stop the pool
        """
        if not self.lvpool.is_started:
            return
        self.lvpool.destroy()

    def to_xml(self):
        """
        Export the pool to xml
        """

        pool = self.controller.get_template("pool.xml").render(pool_name=self.name, basepath=self.controller.base_path)
        return pool

    @classmethod
    def from_xml(cls, controller, source):
        """
        Instantiate a Pool object using the provided xml source and kvm controller object.

        @param controller object(j.sal.kvm.KVMController): controller object to use.
        @param source  str: xml string of pool to be created
        """
        root = ElementTree.fromstring(source)
        name = root.findtext("name")
        path = root.find("target").findtext("path")
        pool = cls(controller, name)
        pool.poolpath = path
        return pool

    @classmethod
    def get_by_name(cls, controller, name):
        pool = controller.connection.storagePoolLookupByName(name)
        return cls.from_xml(controller, pool.XMLDesc())

    def list_disks(self):
        disks = []
        if self.is_started:
            for vol in self.lvpool.listAllVolumes():
                disk = Disk.from_xml(self.controller, vol.XMLDesc())
                disks.append(disk)
        return disks

    @property
    def lvpool(self):
        if not self._lvpool:
            self._lvpool = self.controller.connection.storagePoolLookupByName(self.name)
        return self._lvpool
