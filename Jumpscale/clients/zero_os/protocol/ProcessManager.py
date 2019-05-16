import signal

from . import typchk
from Jumpscale import j


class ProcessManager:
    _process_chk = typchk.Checker({"pid": typchk.Or(int, typchk.IsNone())})

    _kill_chk = typchk.Checker({"pid": int, "signal": int})

    def __init__(self, client):
        self._client = client

    def list(self, id=None):
        """
        List all running processes

        :param id: optional PID for the process to list
        """
        args = {"pid": id}
        self._process_chk.check(args)
        return self._client.json("process.list", args)

    def kill(self, pid, signal=signal.SIGTERM):
        """
        Kill a process with given pid

        :WARNING: beware of what u kill, if u killed redis for example core0 or coreX won't be reachable

        :param pid: PID to kill
        """
        args = {"pid": pid, "signal": int(signal)}
        self._kill_chk.check(args)
        return self._client.json("process.kill", args)
