from Jumpscale import j

from . import typchk


class BtrfsManager:
    _create_chk = typchk.Checker(
        {
            "label": str,
            "metadata": typchk.Enum("raid0", "raid1", "raid5", "raid6", "raid10", "dup", "single", ""),
            "data": typchk.Enum("raid0", "raid1", "raid5", "raid6", "raid10", "dup", "single", ""),
            "devices": typchk.Length([str], 1),
            "overwrite": bool,
        }
    )

    _device_chk = typchk.Checker({"mountpoint": str, "devices": typchk.Length((str,), 1)})

    _subvol_chk = typchk.Checker({"path": str})

    _subvol_quota_chk = typchk.Checker({"path": str, "limit": str})

    _subvol_snapshot_chk = typchk.Checker({"source": str, "destination": str, "read_only": bool})

    def __init__(self, client):
        self._client = client

    def list(self):
        """
        List all btrfs filesystem
        """
        return self._client.json("btrfs.list", {})

    def info(self, mountpoint):
        """
        Get btrfs fs info
        """
        return self._client.json("btrfs.info", {"mountpoint": mountpoint})

    def create(self, label, devices, metadata_profile="", data_profile="", overwrite=False):
        """
        Create a btrfs filesystem with the given label, devices, and profiles
        :param label: name/label
        :param devices : array of devices (/dev/sda1, etc...)
        :metadata_profile: raid0, raid1, raid5, raid6, raid10, dup or single
        :data_profile: same as metadata profile
        :overwrite: force creation of the filesystem. Overwrite any existing filesystem
        """
        args = {
            "label": label,
            "metadata": metadata_profile,
            "data": data_profile,
            "devices": devices,
            "overwrite": overwrite,
        }

        self._create_chk.check(args)
        self._client.sync("btrfs.create", args)

    def device_add(self, mountpoint, *device):
        """
        Add one or more devices to btrfs filesystem mounted under `mountpoint`

        :param mountpoint: mount point of the btrfs system
        :param devices: one ore more devices to add
        :return:
        """
        if len(device) == 0:
            return

        args = {"mountpoint": mountpoint, "devices": device}
        self._device_chk.check(args)
        self._client.sync("btrfs.device_add", args)

    def device_remove(self, mountpoint, *device):
        """
        Remove one or more devices from btrfs filesystem mounted under `mountpoint`

        :param mountpoint: mount point of the btrfs system
        :param devices: one ore more devices to remove
        :return:
        """
        if len(device) == 0:
            return

        args = {"mountpoint": mountpoint, "devices": device}

        self._device_chk.check(args)
        self._client.sync("btrfs.device_remove", args)

    def subvol_create(self, path):
        """
        Create a btrfs subvolume in the specified path
        :param path: path to create
        """
        args = {"path": path}
        self._subvol_chk.check(args)
        self._client.sync("btrfs.subvol_create", args)

    def subvol_list(self, path):
        """
        List a btrfs subvolume in the specified path
        :param path: path to be listed
        """
        return self._client.json("btrfs.subvol_list", {"path": path})

    def subvol_delete(self, path):
        """
        Delete a btrfs subvolume in the specified path
        :param path: path to delete
        """
        args = {"path": path}

        self._subvol_chk.check(args)
        self._client.sync("btrfs.subvol_delete", args)

    def subvol_quota(self, path, limit):
        """
        Apply a quota to a btrfs subvolume in the specified path
        :param path:  path to apply the quota for (it has to be the path of the subvol)
        :param limit: the limit to Apply
        """
        args = {"path": path, "limit": limit}

        self._subvol_quota_chk.check(args)
        self._client.sync("btrfs.subvol_quota", args)

    def subvol_snapshot(self, source, destination, read_only=False):
        """
        Take a snapshot

        :param source: source path of subvol
        :param destination: destination path of snapshot
        :param read_only: Set read-only on the snapshot
        :return:
        """

        args = {"source": source, "destination": destination, "read_only": read_only}

        self._subvol_snapshot_chk.check(args)
        self._client.sync("btrfs.subvol_snapshot", args)
