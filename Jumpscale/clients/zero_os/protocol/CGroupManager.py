from Jumpscale import j
from . import typchk


class CGroupManager:
    _subsystem_chk = typchk.Enum("cpuset", "memory")

    _cgroup_chk = typchk.Checker({"subsystem": _subsystem_chk, "name": str})

    _task_chk = typchk.Checker({"subsystem": _subsystem_chk, "name": str, "pid": int})

    _memory_spec = typchk.Checker({"name": str, "mem": int, "swap": int})

    _cpuset_spec = typchk.Checker(
        {"name": str, "cpus": typchk.Or(typchk.IsNone(), str), "mems": typchk.Or(typchk.IsNone(), str)}
    )

    def __init__(self, client):
        self._client = client

    def list(self):
        """
        List all cgroups names grouped by the cgroup subsystem
        """
        return self._client.json("cgroup.list", {})

    def ensure(self, subsystem, name):
        """
        Creates a cgroup if it doesn't exist under the specified subsystem
        and the given name

        :param subsystem: the cgroup subsystem (currently support 'memory', and 'cpuset')
        :param name: name of the cgroup to delete
        """
        args = {"subsystem": subsystem, "name": name}

        self._cgroup_chk.check(args)
        return self._client.json("cgroup.ensure", args)

    def remove(self, subsystem, name):
        """
        Removes a cgroup by type/name

        :param subsystem: the cgroup subsystem (currently support 'memory', and 'cpuset')
        :param name: name of the cgroup to delete
        """

        args = {"subsystem": subsystem, "name": name}

        self._cgroup_chk.check(args)
        return self._client.json("cgroup.remove", args)

    def tasks(self, subsystem, name):
        """
        List all tasks (PIDs) that are added to this cgroup

        :param subsystem: the cgroup subsystem (currently support 'memory', and 'cpuset')
        :param name: name of the cgroup
        """

        args = {"subsystem": subsystem, "name": name}

        self._cgroup_chk.check(args)
        return self._client.json("cgroup.tasks", args)

    def task_add(self, subsystem, name, pid):
        """
        Add process (with pid) to a cgroup

        :param subsystem: the cgroup subsystem (currently support 'memory', and 'cpuset')
        :param name: name of the cgroup
        :param pid: PID to add
        """

        args = {"subsystem": subsystem, "name": name, "pid": pid}

        self._task_chk.check(args)
        return self._client.json("cgroup.task-add", args)

    def task_remove(self, subsystem, name, pid):
        """
        Remove a process (with pid) from a cgroup

        :param subsystem: the cgroup subsystem (currently support 'memory', and 'cpuset')
        :param name: name of the cgroup
        :param pid: PID to remove
        """

        args = {"subsystem": subsystem, "name": name, "pid": pid}

        self._task_chk.check(args)
        return self._client.json("cgroup.task-remove", args)

    def reset(self, subsystem, name):
        """
        Reset cgroup limitation to default values

        :param subsystem: the cgroup subsystem (currently support 'memory', and 'cpuset')
        :param name: name of the cgroup
        """

        args = {"subsystem": subsystem, "name": name}

        self._cgroup_chk.check(args)
        return self._client.json("cgroup.reset", args)

    def memory(self, name, mem=0, swap=0):
        """
        Set/Get memory cgroup specification/limitation
        the call to this method will always GET the current set values for both mem and swap.
        If mem is not zero, the memory will set the memory limit to the given value, and swap to the given value (even 0)

        :param mem: Set memory limit to the given value (in bytes), ignore if 0
        :param swap: Set swap limit to the given value (in bytes) (only if mem is not zero)

        :return: current memory limitation
        """

        args = {"name": name, "mem": mem, "swap": swap}

        self._memory_spec.check(args)
        return self._client.json("cgroup.memory.spec", args)

    def cpuset(self, name, cpus=None, mems=None):
        """
        Set/Get cpuset cgroup specification/limitation
        the call to this method will always GET the current set values for both cpus and mems
        If cpus, or mems is NOT NONE value it will be set as the spec for that attribute

        :param cpus: Set cpus affinity limit to the given value (0, 1, 0-10, etc...)
        :param mems: Set mems affinity limit to the given value (0, 1, 0-10, etc...)

        :return: current cpuset
        """

        args = {"name": name, "cpus": cpus, "mems": mems}

        self._cpuset_spec.check(args)
        return self._client.json("cgroup.cpuset.spec", args)
