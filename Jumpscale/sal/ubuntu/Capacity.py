import json

import psutil

from Jumpscale import j
from JumpscaleLib.sal_zos.disks.Disks import StorageType


class Capacity:

    def __init__(self, node):
        self._node = node
        self._hw_info = None
        self._disk_info = None
        self._smartmontools_installed = False

    @property
    def hw_info(self):
        if self._hw_info is None:
            self._node.apt_install_check("dmidecode", "dmidecode")

            rc, dmi_data, err = self._node._local.execute("dmidecode", die=False)
            if rc != 0:
                raise RuntimeError("Error getting hardware info:\n%s" % (err))

            self._hw_info = j.tools.capacity.parser.hw_info_from_dmi(dmi_data)
        return self._hw_info

    @property
    def disk_info(self):
        if self._disk_info is None:
            j.tools.prefab.local.monitoring.smartmontools.install()

            self._disk_info = {}

            rc, out, err = self._node._local.execute(
                "lsblk -Jb -o NAME,SIZE,ROTA,TYPE", die=False)
            if rc != 0:
                raise RuntimeError("Error getting disks:\n%s" % (err))

            disks = json.loads(out)["blockdevices"]
            for disk in disks:
                if not disk["name"].startswith("/dev/"):
                    disk["name"] = "/dev/%s" % disk["name"]

                rc, out, err = self._node._local.execute(
                    "smartctl -T permissive -i %s" % disk["name"], die=False)
                if rc != 0:
                    # smartctl prints error on stdout
                    raise RuntimeError("Error getting disk data for %s (Make sure you run this on baremetal, not on a VM):\n%s\n\n%s" % (disk["name"], out, err))

                self._disk_info[disk["name"]] = j.tools.capacity.parser.disk_info_from_smartctl(
                    out,
                    disk["size"],
                    _disk_type(disk).name,
                )
        return self._disk_info

    def report(self, indent=None):
        """
        create a report of the hardware capacity for
        processor, memory, motherboard and disks
        """
        return j.tools.capacity.parser.get_report(psutil.virtual_memory().total, self.hw_info, self.disk_info, indent=indent)

    def get(self, farmer_id):
        """
        get the capacity object of the node

        this capacity object is used in the capacity registration

        :return: dict object ready for capacity registration
        :rtype: dict
        """
        interface, _ = j.sal.nettools.getDefaultIPConfig()
        mac = j.sal.nettools.getMacAddress(interface)
        node_id = mac.replace(':', '')
        if not node_id:
            raise RuntimeError("can't detect node ID")

        report = self.report()
        capacity = dict(
            node_id=node_id,
            location=report.location,
            total_resources=dict(
                cru=report.CRU,
                mru=report.MRU,
                hru=report.HRU,
                sru=report.SRU,
            ),
            robot_address="private",
            os_version="private",
            farmer_id=farmer_id,
            uptime=int(self._node.uptime()),
        )
        return capacity

    def register(self, farmer_id):
        if not farmer_id:
            return False
        data = self.get(farmer_id)
        client = j.clients.threefold_directory.get(interactive=False)
        _, resp = client.api.RegisterCapacity(data)
        resp.raise_for_status()
        return True


def _disk_type(disk_info):
    """
    return the type of the disk
    """
    if disk_info['rota'] == "1":
        if disk_info['type'] == 'rom':
            return StorageType.CDROM
        # assume that if a disk is more than 7TB it's a SMR disk
        elif int(disk_info['size']) > (1024 * 1024 * 1024 * 1024 * 7):
            return StorageType.ARCHIVE
        else:
            return StorageType.HDD
    else:
        if "nvme" in disk_info['name']:
            return StorageType.NVME
        else:
            return StorageType.SSD
