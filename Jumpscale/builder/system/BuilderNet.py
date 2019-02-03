import re
from Jumpscale import j


class BuilderNet(j.builder.system._BaseClass):


    def __init(self):
        self._logger_enable()


    def tcpport_check(self, port, prefix=""):
        res = []
        for item in self.info_get(prefix):
            if item["localport"] == port:
                return True
        return False

    def _info_get(self):
        """
        return
        [$item,]

        $item is dict

        {'local': '0.0.0.0',
         'localport': 6379,
         'pid': 13824,
         'process': 'redis',
         'receive': 0,
         'receivebytes': 0,
         'remote': '0.0.0.0',
         'remoteport': '*',
         'send': 0,
         'sendbytes': 0,
         'parentpid':0}


        """
        result = []
        if "linux" in j.core.platformtype.myplatform.platformtypes:
            cmdlinux = 'netstat -lntp'
            _, out, _ = j.sal.process.execute(cmdlinux, showout=False)
            # to troubleshoot https://regex101.com/#python
            p = re.compile(
                u"tcp *(?P<receive>[0-9]*) *(?P<send>[0-9]*) *(?P<local>[0-9*.]*):(?P<localport>[0-9*]*) *(?P<remote>[0-9.*]*):(?P<remoteport>[0-9*]*) *(?P<state>[A-Z]*) *(?P<pid>[0-9]*)/(?P<process>\w*)")
            for line in out.split("\n"):
                res = re.search(p, line)
                if res is not None:
                    # self._log_info(line)
                    d = res.groupdict()
                    d["process"] = d["process"].lower()
                    if d["state"] == "LISTEN":
                        d.pop("state")
                        result.append(d)
            # now tcp6
            p = re.compile(
                u"tcp6 *(?P<receive>[0-9]*) *(?P<send>[0-9]*) *(?P<local>[0-9*.:]*):(?P<localport>[0-9*]*) *(?P<remote>[0-9.*:]*):(?P<remoteport>[0-9*]*) *(?P<state>[A-Z]*) *(?P<pid>[0-9]*)/(?P<process>\w*)")
            for line in out.split("\n"):
                res = re.search(p, line)
                if res is not None:
                    # self._log_info(line)
                    d = res.groupdict()
                    d["process"] = d["process"].lower()
                    if d["state"] == "LISTEN":
                        d.pop("state")
                        result.append(d)

        elif "darwin" in j.core.platformtype.myplatform.platformtypes:
            # cmd='sudo netstat -anp tcp'
            # # out=j.sal.process.execute(cmd)
            # p = re.compile(u"tcp4 *(?P<rec>[0-9]*) *(?P<send>[0-9]*) *(?P<local>[0-9.*]*) *(?P<remote>[0-9.*]*) *LISTEN")
            cmd = "lsof -i 4tcp -sTCP:LISTEN -FpcRn"
            _, out, _ = j.sal.process.execute(cmd, showout=False)
            d = {}
            for line in out.split("\n"):
                if line.startswith("p"):
                    d = {'local': '', 'localport': 0, 'pid': 0, 'process': '', 'receive': 0, 'receivebytes': 0,
                         'remote': '', 'remoteport': 0, 'send': 0, 'sendbytes': 0, 'parentpid': 0}
                    d["pid"] = int(line[1:])
                if line.startswith("R"):
                    d["parentpid"] = int(line[1:])
                if line.startswith("c"):
                    d["process"] = line[1:].strip()
                if line.startswith("n"):
                    a, b = line.split(":")
                    d["local"] = a[1:].strip()
                    try:
                        d["localport"] = int(b)
                    except BaseException:
                        d["localport"] = 0
                    result.append(d)

        else:
            raise j.exceptions.RuntimeError("platform not supported")

        for d in result:
            for item in ["receive", "send", "pid", "localport", "remoteport"]:
                if d[item] == "*":
                    continue
                else:
                    d[item] = int(d[item])

        return result

    def info_get(self, prefix=""):
        if prefix == "":
            return self._info_get()
        res = []
        for item in self._info_get():
            if item["process"].lower().startswith(prefix):
                res.append(item)
        return res

    def find(self, name, exact=False):
        """Returns the pids of processes with the given name. If exact is `False`
        it will return the list of all processes that start with the given
        `name`."""
        if isinstance(name, bytes):
            name = name.decode()
        is_string = isinstance(name, str)
        # NOTE: ps -A seems to be the only way to not have the grep appearing
        # as well
        RE_SPACES = re.compile("[\s\t]+")
        if "LEDE" in j.core.platformtype.myplatform.osname:
            cmd = "ps w | grep {0} ; true".format(name) if is_string else "ps w"
        else:
            cmd = "ps -A | grep {0} ; true".format(name) if is_string else "ps -A"
        rc, processes, err = j.sal.process.execute(cmd, replaceArgs=False, die=False)

        res = []
        for line in processes.split("\n"):
            if not line.strip():
                continue
            if ' grep ' in line:
                continue

            items_num = 4
            if "LEDE" in j.core.platformtype.myplatform.osname:
                items_num = 5
            line = RE_SPACES.split(line, items_num-1)
            # 3010 pts/1    00:00:07 gunicorn
            # PID  TTY      TIME     CMD
            # 0    1        2        3
            # We skip lines that are not like we expect them (sometimes error
            # message creep up the output)
            if len(line) < 4:
                continue
            if "LEDE" in j.core.platformtype.myplatform.osname:
                pid, __user, __vsz, __stat, command = line
            else:
                pid, tty, time, command = line

            if is_string:
                if pid and ((exact and command == name) or (not exact and command.find(name) >= 0)):
                    if command.find("prefab") == -1:
                        res.append(pid)
            elif name(line) and pid:
                res.append(pid)
        return res

    def kill(self, name, signal=9, exact=False):
        """Kills the given processes with the given name. If exact is `False`
        it will return the list of all processes that start with the given
        `name`."""
        for pid in self.find(name, exact):
            j.sal.process.execute("kill -s {0} {1} ; true".format(signal, pid), showout=False, replaceArgs=False)
