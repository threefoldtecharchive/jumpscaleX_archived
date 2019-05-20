import re

from Jumpscale import j
import sal.disklayout.mount as mount
import sal.disklayout.lsblk as lsblk


_formatters = {
    # specific format command per filesystem.
    "ntfs": lambda name, fstype: "mkfs.ntfs -f {name}".format(name=name)
}

JSBASE = j.application.JSBaseClass


def isValidFS(v):
    return v.startswith("ext") or v in ("btrfs", "ntfs")


def _default_formatter(name, fstype):
    return "mkfs.{fstype} -f {name}".format(fstype=fstype, name=name)


class PartitionError(Exception, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)


class FormatError(Exception, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)


class DiskError(Exception, JSBASE):
    def __init__(self):
        JSBASE.__init__(self)


class BlkInfo(j.application.JSBaseClass):
    def __init__(self, name, type, size, executor):
        self.name = name
        self.type = type
        self.size = int(size)
        self._executor = executor or j.tools.executorLocal
        JSBASE.__init__(self)

    def __str__(self):
        return "%s %s" % (self.name, self.size)

    def __repr__(self):
        return str(self)

    def mount(self):
        """
        Mount partition 
        """
        if self.invalid:
            raise PartitionError("Partition is invalid")
        mnt = mount.Mount(self.name, self.mountpoint, executor=self._executor)
        mnt.mount()
        self.refresh()

    def umount(self):
        """
        Unmount partition
        """
        if self.invalid:
            raise PartitionError("Partition is invalid")
        mnt = mount.Mount(self.name, self.mountpoint, executor=self._executor)
        mnt.umount()
        self.refresh()

    def unsetAutoMount(self):
        """
        remote partition from fstab
        """
        fstab = self._executor.prefab.core.file_read("/etc/fstab").splitlines()
        dirty = False

        for i in range(len(fstab) - 1, -1, -1):
            line = fstab[i]
            if line.startswith("UUID=%s" % self.uuid) or (self.name != "" and line.startswith(self.name)):
                del fstab[i]
                dirty = True

        if not dirty:
            return

        self._executor.prefab.core.file_write("/etc/fstab", "\n".join(fstab), mode="0644")

    def setAutoMount(self, options="defaults", _dump=0, _pass=0):
        """
        Configure partition auto mount `fstab`
        """
        path = self.mountpoint
        if path == "":
            raise RuntimeError("path cannot be empty")
        self._executor.prefab.core.dir_ensure(path)

        fstab = self._executor.prefab.core.file_read("/etc/fstab").splitlines()

        for i in range(len(fstab) - 1, -1, -1):
            line = fstab[i]
            if line.startswith("UUID=%s" % self.uuid):
                del fstab[i]
                dirty = True
                break

        if path is None:
            return

        entry = ("UUID={uuid}\t{path}\t{fstype}" + "\t{options}\t{_dump}\t{_pass}\n").format(
            uuid=self.uuid, path=path, fstype=self.fstype, options=options, _dump=_dump, _pass=_pass
        )

        fstab.append(entry)

        self._executor.prefab.core.file_write("/etc/fstab", "\n".join(fstab), mode="0644")


class DiskInfo(BlkInfo):
    """
    Represents a disk
    """

    def __init__(self, name, size, mountpoint="", fstype="", uuid="", executor=None):
        super(DiskInfo, self).__init__(name, "disk", size, executor=executor)
        self.mountpoint = mountpoint
        self.fstype = fstype
        self.uuid = uuid
        self.partitions = list()
        # self.mirrors=[]
        self.mirror_devices = []
        if self.fstype == "btrfs":
            devsfound = []
            out = self._executor.execute("btrfs filesystem show %s" % self.name)[1]
            for line in out.split("\n"):
                line = line.strip()
                if line.startswith("devid "):
                    dev = line.split("/dev/")[-1]
                    dev = dev.strip(" /")
                    devsfound.append(dev)
            if len(devsfound) > 1:
                # found mirror
                self.mirror_devices = ["/dev/%s" % item for item in devsfound if "/dev/%s" % item != name]

    def _getpart(self):
        rc, ptable, err = self._executor.execute("parted -sm {name} unit B print".format(name=self.name), showout=False)
        read_disk_next = False
        disk = {}
        partitions = []
        for line in ptable.splitlines():
            line = line.strip()
            if line == "BYT;":
                read_disk_next = True
                continue

            parts = line.split(":")
            if read_disk_next:
                # /dev/sdb:8589934592B:scsi:512:512:gpt:ATA VBOX HARDDISK;
                size = int(parts[1][:-1])
                table = parts[5]

                disk.update(size=size, table=table)
                read_disk_next = False
                continue

            # 1:1048576B:2097151B:1048576B:btrfs:primary:;
            partition = {
                "number": int(parts[0]),
                "start": int(parts[1][:-1]),
                "end": int(parts[2][:-1]),
                "flags": parts[6],
            }

            partitions.append(partition)

        disk["partitions"] = partitions
        return disk

    def _findFreeSpot(self, parts, size):
        if size > parts["size"]:
            return
        start = 20 * 1024  # start from 20k offset.
        for partition in parts["partitions"]:
            if partition["start"] - start > size:
                return start, start + size
            start = partition["end"] + 1

        if start + size > parts["size"]:
            return

        return start, start + size

    def format(self, size, force=False):
        """
        Create new partition and format it as configured 

        :size: in bytes

        Note:
        partition info  must contain the following

        filesystem                     = '<fs-type>'
        mountpath                      = '<mount-path>'
        protected                      = 0 or 1
        type                           = data or root or tmp
        """
        parts = self._getpart()
        spot = self._findFreeSpot(parts, size)
        if not spot:
            raise Exception("No enough space on disk to allocate")

        start, end = spot
        try:

            rc, out, err = self._executor.execute(
                ("parted -s {name} -a optimal unit B " + "mkpart primary {start} {end}").format(
                    name=self.name, start=start, end=end
                ),
                showout=False,
                die=False,
            )
            if err != "" and err.find("The closest location we can manage is") != -1:
                numbers = j.data.regex.findAll(r"(\d*B)", err)
                rc, out, err = self._executor.execute(
                    ("parted -s {name} -a optimal unit B " + "mkpart primary {start} {end}").format(
                        name=self.name, start=start, end=numbers[3]
                    ),
                    showout=False,
                )
        except Exception as e:
            raise FormatError(e)

        numbers = [p["number"] for p in parts["partitions"]]
        newparts = self._getpart()
        newnumbers = [p["number"] for p in newparts["partitions"]]
        number = list(set(newnumbers).difference(numbers))[0]

        partition = PartitionInfo(
            name="%s%d" % (self.name, number),
            size=size,
            uuid="",
            fstype="",
            mountpoint="",
            label="",
            device=self,
            executor=self._executor,
        )
        self.partitions.append(partition)
        return partition

    def _clearMBR(self):
        try:
            self._executor.execute("parted -s {name} mktable gpt".format(name=self.name), showout=False)
        except Exception as e:
            raise DiskError(e)

    def erase(self, force=False):
        """
        Clean up disk by deleting all non protected partitions
        if force=True, delete ALL partitions included protected

        :force: delete protected partitions, default=False
        """
        if force:
            self._clearMBR()
            return

        for partition in self.partitions:
            if not partition.protected:
                partition.delete()

    def unallocatedSpace(self, minimum_size=102400):
        """
        look into the disk for unallocated space.
        return a list of tuple containing start,end of the space

        :minimum_size: unallocated space smaller than this valid are skipt. in bytes
        """
        try:
            rc, out, err = self._executor.execute(
                "parted -m {name} unit B print free".format(name=self.name), showout=False
            )
        except Exception as e:
            raise DiskError(e)

        if err != "" and err.find("unrecognised disk label") != -1:
            # not table set on the disk yet
            self._clearMBR()
            self.unallocatedSpace(minimum_size=minimum_size)

        read_disk_next = False
        free_spaces = []
        for line in out.splitlines():
            line = line.strip()
            if line == "BYT;":
                read_disk_next = True
                continue

            if read_disk_next:
                read_disk_next = False
                continue

            parts = line.split(":")
            # 2:2097152B:20972568575B:20970471424B:ext4:primary:;
            # 1:20972568576B:1999858827263B:1978886258688B:free;
            if parts[4][:-1] != "free":
                continue

            size = int(parts[3][:-1])
            if size < minimum_size:
                continue

            free_space = (int(parts[1][:-1]), int(parts[2][:-1]))

            free_spaces.append(free_space)

        return free_spaces


class PartitionInfo(BlkInfo):
    def __init__(self, name, size, uuid, fstype, mountpoint, label, device, executor=None):
        super(PartitionInfo, self).__init__(name, "part", size, executor=executor)
        self.uuid = uuid
        self.fstype = fstype
        self.mountpoint = mountpoint
        self.label = label
        self.config = {}
        self.device = device
        self._invalid = False

        # self.mount = device.mount

    @property
    def invalid(self):
        return self._invalid

    @property
    def protected(self):
        if self.config == {}:
            # that's an unmanaged partition, assume protected
            return True
        # TODO: implement
        return self.config.get("protected", True)

    def _formatter(self, name, fstype):
        fmtr = _formatters.get(fstype, _default_formatter)
        return fmtr(name, fstype)

    def refresh(self):
        """
        Reload partition status to match current real state
        """
        try:
            info = lsblk.lsblk(self.name, executor=self._executor)[0]
            info["label"] = info.pop("PARTLABEL")
        except lsblk.LsblkError:
            self._invalid = True
            info = {"SIZE": 0, "UUID": "", "FSTYPE": "", "MOUNTPOINT": "", "PARTLABEL": ""}

        for key, val in info.items():
            setattr(self, key.lower(), val)

    def format(self, fstype, force=False):
        """
        Reformat the partition
        """
        self.refresh()

        if self.invalid:
            raise PartitionError("Partition is invalid")

        if self.mountpoint:
            if not force:
                raise PartitionError("Partition is mounted on %s" % self.mountpoint)
            else:
                self.umount()

        command = self._formatter(self.name, fstype)
        self.refresh()

    def delete(self, force=False):
        """
        Delete partition

        :force: Force delete protected partitions, default False
        """
        if self.invalid:
            raise PartitionError("Partition is invalid")

        if self.mountpoint:
            raise PartitionError("Partition is mounted on %s" % self.mountpoint)

        if self.protected and not force:
            raise PartitionError("Partition is protected")

        m = re.match("^(.+)(\d+)$", self.name)
        number = int(m.group(2))
        device = m.group(1)

        command = "parted -s {device} rm {number}".format(device=device, number=number)
        try:
            self._executor.execute(command, showout=False)
        except Exception as e:
            raise PartitionError(e)

        self.unsetAutoMount()

        self._invalid = True
        self.device.partitions.remove(self)
