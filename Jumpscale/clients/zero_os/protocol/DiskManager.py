import json

from . import typchk
from Jumpscale import j


class DiskManager:
    _mktable_chk = typchk.Checker(
        {
            "disk": str,
            "table_type": typchk.Enum("aix", "amiga", "bsd", "dvh", "gpt", "mac", "msdos", "pc98", "sun", "loop"),
        }
    )

    _mkpart_chk = typchk.Checker(
        {
            "disk": str,
            "start": typchk.Or(int, str),
            "end": typchk.Or(int, str),
            "part_type": typchk.Enum("primary", "logical", "extended"),
        }
    )

    _getpart_chk = typchk.Checker({"disk": str, "part": str})

    _rmpart_chk = typchk.Checker({"disk": str, "number": int})

    _mount_chk = typchk.Checker({"options": str, "source": str, "target": str})

    _umount_chk = typchk.Checker({"source": str})

    _smartctl_chk = typchk.Checker({"disk": str})

    _spindown_chk = typchk.Checker({"disk": str, "spindown": int})

    _seektime_chk = typchk.Checker({"disk": str})

    def __init__(self, client):
        self._client = client

    def list(self):
        """
        List available block devices
        """
        response = self._client.raw("disk.list", {})

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to list disks: %s" % result.stderr)

        if result.level != 20:  # 20 is JSON output.
            raise j.exceptions.Base("invalid response type from disk.list command")

        data = result.data.strip()
        if data:
            js_data = json.loads(data)
            if "blockdevices" in js_data:
                return js_data["blockdevices"]

            return js_data

        return {}

    def mktable(self, disk, table_type="gpt"):
        """
        Make partition table on block device.
        :param disk: device name (sda, sdb, etc...)
        :param table_type: Partition table type as accepted by parted
        """
        args = {"disk": disk, "table_type": table_type}

        self._mktable_chk.check(args)

        response = self._client.raw("disk.mktable", args)

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to create table: %s" % result.stderr)

    def getinfo(self, disk, part=""):
        """
        Get more info about a disk or a disk partition

        :param disk: (sda, sdb, etc..)
        :param part: (sda1, sdb2, etc...)
        :return: a dict with {"blocksize", "start", "size", and "free" sections}
        """
        args = {"disk": disk, "part": part}

        self._getpart_chk.check(args)

        response = self._client.raw("disk.getinfo", args)

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to get info: %s" % result.data)

        if result.level != 20:  # 20 is JSON output.
            raise j.exceptions.Base("invalid response type from disk.getinfo command")

        data = result.data.strip()
        if data:
            return json.loads(data)
        else:
            return {}

    def mkpart(self, disk, start, end, part_type="primary"):
        """
        Make partition on disk
        :param disk: device name (sda, sdb, etc...)
        :param start: partition start as accepted by parted mkpart
        :param end: partition end as accepted by parted mkpart
        :param part_type: partition type as accepted by parted mkpart
        """
        args = {"disk": disk, "start": start, "end": end, "part_type": part_type}

        self._mkpart_chk.check(args)

        response = self._client.raw("disk.mkpart", args)

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to create partition: %s" % result.stderr)

    def rmpart(self, disk, number):
        """
        Remove partion from disk
        :param disk: device name (sda, sdb, etc...)
        :param number: Partition number (starting from 1)
        """
        args = {"disk": disk, "number": number}

        self._rmpart_chk.check(args)

        response = self._client.raw("disk.rmpart", args)

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to remove partition: %s" % result.stderr)

    def mount(self, source, target, options=[]):
        """
        Mount partion on target
        :param source: Full partition path like /dev/sda1
        :param target: Mount point
        :param options: Optional mount options
        """

        if len(options) == 0:
            options = [""]

        args = {"options": ",".join(options), "source": source, "target": target}

        self._mount_chk.check(args)
        response = self._client.raw("disk.mount", args)

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to mount partition: %s" % result.stderr)

    def umount(self, source):
        """
        Unmount partion
        :param source: Full partition path like /dev/sda1
        """

        args = {"source": source}
        self._umount_chk.check(args)

        response = self._client.raw("disk.umount", args)

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to umount partition: %s" % result.stderr)

    def mounts(self):
        """
        Get all devices and their mountpoints
        """
        response = self._client.raw("disk.mounts", {})

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to list disks: %s" % result.stderr)

        if result.level != 20:  # 20 is JSON output.
            raise j.exceptions.Base("invalid response type from disk.list command")

        data = result.data.strip()
        if data:
            return json.loads(data)
        else:
            return {}

    def smartctl_info(self, disk):
        """
        Info from running smartctl -i <disk>
        :param disk: disk path
        """

        args = {"disk": disk}
        self._smartctl_chk.check(args)

        response = self._client.raw("disk.smartctl-info", args)

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to get smartctl info: %s" % result.stderr)

        if result.level != 20:  # 20 is JSON output.
            raise j.exceptions.Base("invalid response type from disk.list command")

        data = result.data.strip()
        if data:
            return json.loads(data)
        else:
            return {}

    def smartctl_health(self, disk):
        """
        Info from running smartctl -H <disk>
        :param disk: disk path
        """

        args = {"disk": disk}
        self._smartctl_chk.check(args)

        response = self._client.raw("disk.smartctl-health", args)

        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to get smartctl info: %s" % result.stderr)

        if result.level != 20:  # 20 is JSON output.
            raise j.exceptions.Base("invalid response type from disk.list command")

        data = result.data.strip()
        if data:
            return json.loads(data)
        else:
            return {}

    def spindown(self, disk, spindown=1):
        """
        Spindown a disk
        :param disk str: Full path to a disk like /dev/sda
        :param spindown int: spindown value should be in [1, 240]
        """
        args = {"disk": disk, "spindown": spindown}
        self._spindown_chk.check(args)
        response = self._client.raw("disk.spindown", args)

        result = response.get()
        if result.state != "SUCCESS":
            raise j.exceptions.Base("Failed to spindown disk {} to {}.".format(disk, spindown))

    def isstandby(self, disk):
        """
        Verify if a disk is powered down (i.e. it's still available, but went
        in standby mode, and stopped spinning after spindown (see above) interval)
        NOTE: default of spindown is 1, so after 5 seconds, and not accessed the disk
        will stop spinning
        :param disk str: Full path to a disk like /dev/sda
        """
        args = {"disk": disk}
        self._isstandby_chk.check(args)

        return self._client.json("disk.isstandby", args)

    def seektime(self, disk):
        """
        Gives seek latency on disk which is a very good indication to the `type` of the disk.
        it's a very good way to verify if the underlying disk type is SSD or HDD

        :param disk: disk path or name (/dev/sda, or sda)
        :return: a dict as follows {'device': '<device-path>', 'elapsed': <seek-time in us', 'type': '<SSD or HDD>'}
        """
        args = {"disk": disk}

        self._seektime_chk.check(args)

        return self._client.json("disk.seektime", args)
