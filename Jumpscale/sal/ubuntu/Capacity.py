import json
import psutil
from Jumpscale import j


class Capacity:
    def __init__(self, node):
        self._node = node
        self._hw_info = None
        self._disk_info = None
        self._memory_info = None
        self._smartmontools_installed = False

    @property
    def hw_info(self):
        """dump a computer's DMI (some say SMBIOS) table contents in a human-readable.

        :raise j.exceptions.Base: Error getting hardware info from dmidecode
        :return: the hardware info
        :rtype: str
        """
        if self._hw_info is None:
            self._node.apt_install_check("dmidecode", "dmidecode")

            rc, dmi_data, err = j.sal.process.execute("dmidecode", die=False)
            if rc != 0:
                raise j.exceptions.Base("Error getting hardware info:\n%s" % (err))

            self._hw_info = j.tools.capacity.parser.hw_info_from_dmi(dmi_data)
        return self._hw_info

    @property
    def disk_info(self):
        """get information about all available or the specified block devices.

        :return: disk information
        :rtype: str
        """
        if self._disk_info is None:
            j.builders.monitoring.smartmontools.install()

            self._disk_info = {}

            rc, out, err = j.sal.process.execute("lsblk -Jb -o NAME,SIZE,ROTA,TYPE", die=False)
            if rc != 0:
                raise j.exceptions.Base("Error getting disks:\n%s" % (err))

            disks = json.loads(out)["blockdevices"]
            for disk in disks:
                if not disk["name"].startswith("/dev/"):
                    disk["name"] = "/dev/%s" % disk["name"]

                rc, out, err = j.sal.process.execute("smartctl -T permissive -i %s" % disk["name"], die=False)
                if rc != 0:
                    # smartctl prints error on stdout
                    raise j.exceptions.Base(
                        "Error getting disk data for %s (Make sure you run this on baremetal, not on a VM):\n%s\n\n%s"
                        % (disk["name"], out, err)
                    )

                self._disk_info[disk["name"]] = j.tools.capacity.parser.disk_info_from_smartctl(
                    out, disk["size"], _disk_type(disk).name
                )
        return self._disk_info

    @property
    def memory_info(self):
        """get the total memeory information.

        :return: the memory total information
        :rtype: str
        """

        if self._memory_info is None:
            self._memory_info = psutil.virtual_memory().total
        return self._memory_info

    def report(self, indent=None):
        """
        create a report of the hardware capacity for
        processor, memory, motherboard and disks

        :param indent: json indent for pretty printing
        :type indent: int
        :return: report for the hardware capacity information
        :rtype: report
        """
        return j.tools.capacity.parser.get_report(self._memory_info, self.hw_info, self.disk_info, indent=indent)

    def get(self, farmer_id):
        """get the capacity object of the node. This capacity object is used in the capacity registration

        :param farmer_id: farmer id value
        :type: str
        :return: dict object ready for capacity registration
        :rtype: dict
        """
        interface, _ = j.sal.nettools.getDefaultIPConfig()
        mac = j.sal.nettools.getMacAddress(interface)
        node_id = mac.replace(":", "")
        if not node_id:
            raise j.exceptions.Base("can't detect node ID")

        report = self.report()
        capacity = dict(
            node_id=node_id,
            location=report.location,
            total_resources=dict(cru=report.CRU, mru=report.MRU, hru=report.HRU, sru=report.SRU),
            robot_address="private",
            os_version="private",
            farmer_id=farmer_id,
            uptime=int(self._node.uptime()),
        )
        return capacity

    def register(self, farmer_id):
        """register the node

        :param farmer_id: farmer id value
        :type: str
        :return: If registration done, return True, else return False
        :rtype: bool
        """
        if not farmer_id:
            return False
        data = self.get(farmer_id)
        client = j.clients.threefold_directory.get(interactive=False)
        _, resp = client.api.RegisterCapacity(data)
        resp.raise_for_status()
        return True


def _disk_type(disk_info):
    """get the type of the disk.

    :return: the type of the disk
    :rtype: str
    """
    # @todo from sal_zos.disks.Disks import StorageType
    if disk_info["rota"] == "1":
        if disk_info["type"] == "rom":
            # @todo return StorageType.CDROM
            return "CDROM"
        # assume that if a disk is more than 7TB it's a SMR disk
        elif int(disk_info["size"]) > (1024 * 1024 * 1024 * 1024 * 7):
            # @todo return StorageType.ARCHIVE
            return "ARCHIVE"
        else:
            # @todo return StorageType.HDD
            return "HDD"
    else:
        if "nvme" in disk_info["name"]:
            # @todo return StorageType.NVME
            return "NVME"

        else:
            # @todo return StorageType.SSD
            return "SDD"
