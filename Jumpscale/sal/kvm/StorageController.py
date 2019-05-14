from Jumpscale import j
from sal.kvm.BaseKVMComponent import BaseKVMComponent


class StorageController(BaseKVMComponent):
    def __init__(self, controller):
        self.controller = controller
        BaseKVMComponent.__init__(controller=controller)

    def get_pool(self, pool_name):
        """
        Get pool
        """

        try:
            storagepool = self.controller.connection.storagePoolLookupByName(pool_name)
            return storagepool
        except BaseException:
            return None

    def create_pool(self, pool):
        """
        @pool pool: pool object to create pool from
        Create pool in libvirt
        """

        self.controller.executor.prefab.core.dir_ensure(pool.poolpath)
        cmd = "chattr +C %s " % pool.poolpath
        self.controller.executor.execute(cmd)
        self.controller.connection.storagePoolCreateXML(pool.to_xml(), 0)

    def delete_pool(self, pootname):
        """
        Delet pool
        """

        pool = self.get_pool(pool_name)
        if pool is not None:
            # destroy the pool
            pool.undefined()

    def get_or_create_pool(self, pool_name):
        """
        get or create bool if it does not exists
        """

        if pool_name not in self.controller.connection.listStoragePools():
            poolpath = self.controller.executor.prefab.core.joinpaths(self.controller.base_path, pool_name)
            if not self.controller.executor.prefab.core.dir_exists(poolpath):
                self.controller.executor.prefab.core.dir_ensure(poolpath)
                cmd = "chattr +C %s " % poolpath
                self.controller.executor.execute(cmd)
            pool = self.controller.get_template("pool.xml").render(
                pool_name=pool_name, basepath=self.controller.base_path
            )
            self._log_debug(pool)
            self.controller.connection.storagePoolCreateXML(pool, 0)
        storagepool = self.controller.connection.storagePoolLookupByName(pool_name)
        return storagepool

    def list_pools(self):
        """
        List all pools
        """
        from sal.kvm.Pool import Pool

        pools = []
        for pool_kvm in self.controller.connection.listAllStoragePools():
            pools.append(Pool.from_xml(controller=self.controller, source=pool_kvm.XMLDesc()))
        return pools

    def list_disks(self, pool_name=None):
        """
        List all disks from all pools

        @param pool_name string: if specified, only return disks from this pool
        """

        disks = []
        for pool in self.controller.connection.listAllStoragePools():
            if pool.isActive():
                for vol in pool.listAllVolumes():
                    disk = Disk.from_xml(self.controller, vol.XMLDesc())
                    disks.append(disk)
        return disks
