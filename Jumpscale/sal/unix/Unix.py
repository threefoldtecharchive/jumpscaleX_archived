import os
import re
import grp
import pwd
import subprocess
import sys
import math

from Jumpscale import j
from Jumpscale.data.time.TimeInterval import TimeInterval as TimeIntervalUnit

# from core.decorators import deprecated

# TODO: *3 fix, move to other sal's

# TODO: cron needs to be moved into SAL
# TODO: move many of these methods to prefab2 (our prefab) or to system if more appropriate
# TODO: this file needs to go away
# TODO: make sure we use proper names & add to right prefab module
JSBASE = j.application.JSBaseClass


def user_in_group(username, groupname):
    """Check whether a given user is member of a given group

    @param username: Name of the user to check
    @type username: string
    @param groupname: Name of the group to check
    @type groupname: string

    @returns: Whether the user is member of the group
    @rtype: bool

    @raises KeyError: Unknown username or groupname
    """
    # Retieve information of the group
    group = grp.getgrnam(groupname)
    # Check whether the user is member of the group
    if username in group.gr_mem:
        return True

    # If the user is not member of the group, the given group might still be
    # the primary group of the user
    # Retrieve user information
    user = pwd.getpwnam(username)
    # Compare GIDs
    return user.pw_gid == group.gr_gid


class UnixSystem(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.sal.unix"
        JSBASE.__init__(self)

    def getBashEnvFromFile(self, file, var):
        """Get the value of an environment variable in a Bash file

        @param file: Bash file defining the variable
        @type file: string
        @param var: Variable name
        @type var: string
        """
        # TODO: there are better ways of doing this
        exitcode, output, err = j.sal.process.execute(". %s > /dev/null && echo $%s" % (file, var), useShell=True)
        if exitcode != 0:
            return ""
        else:
            return output[:-1]

    def getMachineInfo(self):
        """Get memory and CPU info about this machine

        @returns: Amount of available memory in (MBs), Average CPU speed in (MHz) and number of CPUs
        @rtype: tuple
        """
        mem = 0
        cpumhz = 0
        nrcpu = 0
        if j.core.platformtype.myplatform.platform_is_linux or j.core.platformtype.myplatform.isESX():
            memcontent = j.sal.fs.readFile("/proc/meminfo")
            match = re.search("^MemTotal\:\s+(\d+)\s+kB$", memcontent, re.MULTILINE)
            if match:
                # algorithme to round the memory again
                mem_in_gb = int(match.group(1)) / (1024.0 ** 2)
                percisions = 2  # means 1 / 2 GB precision
                # we use ceil because we can only loose memory used by system
                mem = int((math.ceil((mem_in_gb * percisions)) / percisions) * 1024)
            cpucontent = j.sal.fs.readFile("/proc/cpuinfo")
            matches = re.findall("^cpu\sMHz\s+:\s(\d+)\.\d+$", cpucontent, re.MULTILINE)
            if matches:
                int_values = [int(x) for x in matches]
                nrcpu = len(matches)
                cpumhz = int(sum(int_values) / nrcpu)  # get average of CPUs speeds
            return mem, cpumhz, nrcpu
        elif j.core.platformtype.myplatform.isSolaris():
            command = "prtconf | grep Memory | awk '{print $3}'"
            exitcoude, output, err = j.sal.process.execute(command, useShell=True)
            mem = output.strip()
            command = "psrinfo -v | grep 'processor operates' | awk '{print $6}'"
            exitcoude, output, err = j.sal.process.execute(command, useShell=True)
            tuples = output.strip().split("\n")
            nrcpu = len(tuples)
            cpumhz = int(tuples[0])
            return mem, cpumhz, nrcpu
        else:
            raise j.exceptions.RuntimeError(" System.getMachineInfo not supported on this platform")

    def addCronJob(
        self,
        commandToExecute,
        interval=1,
        logFilePath=None,
        replaceLineIfCommandAlreadyInCrontab=True,
        unit=TimeIntervalUnit.MINUTES,
    ):
        """Add a cronjob to the system

        @param commandToExecute: The command to execute
        @type commandToExecute: string
        @param interval: The interval at which to launch the commandToExecute
        @type interval: number
        @param logFilePath: the path of the logfile to redirect the output of crontab to
        @type logFilePath: string
        @param replaceLineIfCommandAlreadyInCrontab: Specifies whether to replace the line if a command already exists in crontab
        @type replaceLineIfCommandAlreadyInCrontab: bool
        @param unit: The unit of the interval
        @type unit: TimeIntervalUnit
        """

        if not pwd.getpwuid(os.getuid())[0] == "root":
            raise j.exceptions.RuntimeError("You have to be logged in as root to add a CronJob.")

        # Configuration dependent on the time interval
        if unit == TimeIntervalUnit.MINUTES:
            allowedIntervals = [1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30]
            unitRange = 60
            startAt = 0
            unitPlace = 1
        elif unit == TimeIntervalUnit.HOURS:
            allowedIntervals = [1, 2, 3, 4, 6, 8, 12]
            unitRange = 24
            startAt = 0
            unitPlace = 2
        elif unit == TimeIntervalUnit.DAYS:
            allowedIntervals = list(range(1, 16))  # 1,2,...,16
            unitRange = 31
            startAt = 1
            unitPlace = 3
        elif unit == TimeIntervalUnit.MONTHS:
            allowedIntervals = [1, 2, 3, 4, 6]
            unitRange = 12
            startAt = 1
            unitPlace = 4
        else:
            raise ValueError("This function only supports these interval units: minutes, hours, days and months.")

        if interval not in allowedIntervals:
            raise ValueError("This function only supports following intervals: " + str(allowedIntervals))

        # Construct timing options
        if j.core.platformtype.myplatform.platform_is_linux:
            crontabFilePath = "/etc/crontab"
            crontabItem = "*/" + str(interval)
        else:
            raise j.exceptions.RuntimeError("Platform not supported.")

        # These lines generate strings like "0 0 */3 * * " specifing options for the crontab command.
        # Execute command between x:00 and x:59 if they run hourly, between 0:00
        # and 2:59 if they run daily and on any day if they run monthly.
        randomRanges = [(0, 60), (0, 3), (1, 29)]
        import random

        crontabOptions = " ".join([str(random.randrange(t[0], t[1])) for t in randomRanges[: (unitPlace - 1)]])
        if not unitPlace == 1:
            crontabOptions = crontabOptions + " "
        crontabOptions = crontabOptions + crontabItem + " "
        crontabOptions = crontabOptions + "* " * (5 - unitPlace)
        if j.core.platformtype.myplatform.platform_is_linux:
            # The Vixie cron (for Linux) has an extra option: username of running process.
            crontabOptions = crontabOptions + "root    "

        # Construct output redirection
        if logFilePath is None:
            crontabOutputRedir = " >/dev/null"
        else:
            if not j.sal.fs.exists(j.sal.fs.getDirName(logFilePath)):
                j.sal.fs.createDir(j.sal.fs.getDirName(logFilePath))
            crontabOutputRedir = " >>" + logFilePath
        crontabOutputRedir = crontabOutputRedir + " 2>&1"

        # Check if command already present.
        crontabLines = j.sal.fs.readFile(crontabFilePath).splitlines()
        commandFoundInCrontab = -1
        for i in range(len(crontabLines)):
            if crontabLines[i].find(commandToExecute) > -1 and not crontabLines[i].lstrip().startswith("#"):
                commandFoundInCrontab = i

        if commandFoundInCrontab == -1 or not replaceLineIfCommandAlreadyInCrontab:
            crontabLines.append(crontabOptions + commandToExecute + crontabOutputRedir)
            crontabLines.append("")  # Adding second newline at the end, see BUGS section in crontab man page.
        else:
            # replace existing line, maybe the timing options or output redirection have changed.
            crontabLines[commandFoundInCrontab] = crontabOptions + commandToExecute + crontabOutputRedir

        # Backup old crontab file and write modifications new crontab file.
        j.sal.fs.copyFile(crontabFilePath, crontabFilePath + ".backup")  # Create backup
        if j.core.platformtype.myplatform.platform_is_linux:
            # On Linux, we edit the system-wide crontab of Vixie Cron, so don't have
            # to run the "crontab" command to be sure changes have effect.
            j.sal.fs.writeFile(crontabFilePath, "\n".join(crontabLines) + "\n")
        else:
            raise j.exceptions.RuntimeError("Platform not supported.")

    def killGroup(self, pid):
        """ Kill a process group

        killGroup will get the parent pid from the pid given and kill the group with signal SIGKILL (default)

        @type pid: int
        @param pid: process id
        """

        self._log_info("Killing process group of %d" % pid)
        import signal

        os.killpg(os.getpgid(pid), signal.SIGKILL)

    def chown(self, path, user, group, recursive=False):
        """
        Chown a file
        @param path: the path of a file or a directory to be chown
        @type path: string
        @param user: username to be used as the new owner
        @type user: string
        @param group: groupname to be used as the new group owner (if None, then root is used as a groupname0
        @type group: string
        @param recursive: if path is a directory, all files underneath the path are also chown if True (default False)
        @type recursive: boolean
        """
        if not group:
            group = "root"
        self._log_info("Chown %s:%s %s" % (user, group, path))
        uid = pwd.getpwnam(user).pw_uid
        if group is None:
            gid = grp.getgrnam(group).gr_gid
        else:
            gid = grp.getgrnam(group).gr_gid
        os.chown(path, uid, gid)
        if recursive:

            def process_path(arg, path):
                os.chown(path, uid, gid)

            j.sal.fswalker.walk(path, process_path, recursive=True, includeFolders=True)

    def chmod(self, root, mode, recurse=0, dirPattern="*", filePattern="*", dirs=True, files=True):
        """
        Chmod based on system.fs.walk
        """
        self._log_info("Chmod %s" % root)
        if j.sal.fs.isFile(root):
            os.chmod(root, mode)
        else:
            items = j.sal.fswalker.walkExtended(
                root=root, recurse=recurse, dirPattern=dirPattern, filePattern=filePattern, dirs=dirs, files=files
            )

            for item in items:
                os.chmod(item, mode)

    def executeAsUser(self, command, username, **kwargs):
        """Execute a given command as a specific user

        When calling this method, the command will be wrapped inside 'su' to
        be executed as some specific user. This requires the application which
        spawns the command to be running as root.

        Next to this, it behaves exactly as C{j.sal.process.execute},
        including the same named arguments.

        @param command: Command to execute
        @type command: string
        @param username: Name of the user to impersonate
        @type username: string

        @returns: Exit code and command output
        @rtype: tuple

        @raises RuntimeError: When the application is not running as root
        @raises RuntimeError: If /bin/su is not available on the system
        @raises ValueError: When the provided username can't be resolved

        @see: system.process.SystemProcess.execute
        """
        command = self._prepareCommand(command, username)

        kwargs = kwargs.copy()
        kwargs["command"] = command

        return j.sal.process.execute(**kwargs)

    # @deprecated('j.sal.unix.executeDaemonAsUser',
    #            alternative='j.sal.process.executeDaemon', version='3.2')
    def executeDaemonAsUser(self, command, username, **kwargs):
        """Execute a given command as a background process as a specific user

        When calling this method, the command will be wrapped inside 'su' to
        be executed as some specific user. This requires the application which
        spawns the command to be running as root.

        Next to this, it behaves exactly as C{j.sal.process.executeDaemon},
        including the same named arguments.

        @param command: Command to execute
        @type command: string
        @param username: Name of the user to impersonate
        @type username: string

        @returns: pid of the process
        @rtype: int

        @raises RuntimeError: When the application is not running as root
        @raises RuntimeError: If /bin/su is not available on the system
        @raises ValueError: When the provided username can't be resolved

        @see: system.process.runDaemon
        """

        command = self._prepareCommand(command, username)
        kwargs = kwargs.copy()
        kwargs["commandline"] = command

        return j.sal.process.executeDaemon(**kwargs)

    def _mkarg(self, string):
        """
        Converts string to a shell command argument
        Note:
            Removed from python commands library, implementation found at https://hg.python.org/cpython/file/67318d3fa6dc/Lib/commands.py
        """
        if "'" not in string:
            return " '" + string + "'"
        s = ' "'
        for c in string:
            if c in '\\$"`':
                s = s + "\\"
            s = s + c
        s = s + '"'
        return s

    def _prepareCommand(self, command, username):
        self._log_debug("Attempt to run %s as user %s" % (command, username))
        try:
            pwent = pwd.getpwnam(username)
        except KeyError:
            raise ValueError("The user %s can't be found on this system" % username)

        if not os.getuid() == 0:
            raise j.exceptions.RuntimeError("Can't execute as user when not running as root (UID 0)")

        subin = "/bin/su"

        if not j.sal.fs.exists(subin):
            raise j.exceptions.RuntimeError("%s not found on this system, I need it there" % subin)

        command = "%s --login --command %s %s" % (subin, self._mkarg(command), username)

        return command

    def chroot(self, path):
        """Change root directory path

        @param path: Path to chroot() to
        @type path: string
        """
        if not path or not j.sal.fs.checkDirParam(path):
            raise ValueError("Path %s is invalid" % path)

        self._log_info("Change root to %s" % path)
        os.chroot(path)

    def addSystemUser(self, username, groupname=None, shell="/bin/bash", homedir=None):
        """Add a user to the system

        Note: you should be root to run this python command.

        @param username: Username of the user to add
        @param groupname: Optional param to add user to existing systemgroup
        @param shell: Optional param to specify the shell of the user
        @type username: string
        """

        if not j.sal.unix.unixUserExists(username):
            self._log_info("User [%s] does not exist, creating an entry" % username)

            command = "useradd"
            options = []
            if groupname and not j.sal.unix.unixGroupExists(groupname):
                raise j.exceptions.RuntimeError("Failed to add user because group %s does not exist" % groupname)
            if groupname and j.sal.unix.unixGroupExists(groupname):
                options.append("-g %s" % (groupname))
            if shell:
                options.append("-s %s" % shell)
            if homedir:
                options.append("-d '%s'" % homedir)
            command = "%s %s %s" % (command, " ".join(options), username)
            exitCode, stdout, stderr = j.sal.process.execute(command)

            if exitCode:
                output = "\n".join(("Stdout:", stdout, "Stderr:", stderr))
                raise j.exceptions.RuntimeError("Failed to add user %s, error: %s" % (username, output))
            if homedir is not None:
                j.sal.fs.createDir(homedir)
                j.sal.fs.chown(homedir, username)
                j.sal.fs.chmod(homedir, 0o700)

        else:
            self._log_warning("User %s already exists" % username)

    def addSystemGroup(self, groupname):
        """ Add a group to the system

        Note: you should be root to run this python command.

        @param groupname: Name of the group to add
        @type groupname : string
        """
        if not j.sal.unix.unixGroupExists(groupname):
            self._log_info("Group [%s] does not exist, creating an entry" % groupname)
            exitCode, stdout, stderr = j.sal.process.execute("groupadd %s" % groupname)

            if exitCode:
                output = "\n".join(("Stdout:", stdout, "Stderr:", stderr))
                raise j.exceptions.RuntimeError("Failed to add group %s, error: %s" % (groupname, output))
        else:
            self._log_warning("Group %s already exists" % groupname)

    def addUserToGroup(self, username, groupname):
        assert j.sal.unix.unixUserExists(username), '"%s" user does not exist' % username

        assert j.sal.unix.unixGroupExists(groupname), '"%s" group does not exist"' % groupname

        j.sal.process.execute("gpasswd -a {username} {groupname}".format(username=username, groupname=groupname))

    def unixUserExists(self, username):
        """Checks if a given user already exists in the system

        @param username: Username of the user to check for
        @type username: string

        @returns: Whether the user exists
        @rtype: bool
        """
        try:
            pwd.getpwnam(username)
        except KeyError:
            return False
        return True

    def unixGroupExists(self, groupname):
        """Checks if a given group already exists in the system

        @param groupname: Name of the group to check for
        @type groupname: string

        @returns: Whether the group exists
        @rtype: bool
        """
        try:
            grp.getgrnam(groupname)
        except KeyError:
            return False
        return True

    def crypt(self, word, salt=None):
        """
        Return a string representing the one-way hash of a password, with a salt
        prepended.
        """
        try:
            import crypt
        except ImportError:
            import fcrypt as crypt
            import string
            from random import SystemRandom

            salt = j.data.idgenerator.generateXCharID(2)

        return crypt.crypt(word, salt)

    def disableUnixUser(self, username):
        """Disables a given unix user

        @param username: Name of the user to disable
        @type username: string

        """
        if not j.sal.unix.unixUserExists(username):
            raise ValueError("User [%s] does not exist, cannot disable user" % username)
        else:
            command = "passwd %s -l" % username
            exitCode, stdout, stderr = j.sal.process.execute(command)

            if exitCode:
                output = "\n".join(("Stdout:", stdout, "Stderr:", stderr))
                raise j.exceptions.RuntimeError("Failed to disable user %s, error: %s" % (username, output))
            return True

    def enableUnixUser(self, username):
        """Enables a given unix user

        @param username: Name of the user to enable
        @type username: string

        """
        if not j.sal.unix.unixUserExists(username):
            raise ValueError("User [%s] does not exist, cannot enable user" % username)
        else:
            command = "passwd %s -u" % username
            exitCode, stdout, stderr = j.sal.process.execute(command)

            if exitCode:
                output = "\n".join(("Stdout:", stdout, "Stderr:", stderr))
                raise j.exceptions.RuntimeError("Failed to enable user %s, error: %s" % (username, output))
            return True

    def removeUnixUser(self, username, removehome=False, die=True):
        """Remove a given unix user

        @param username: Name of the user to remove
        @type username: string

        """
        if not j.sal.unix.unixUserExists(username):
            if die:
                raise ValueError("User [%s] does not exist, cannot remove user" % username)
            else:
                return True
        else:
            removehome = "-r" if removehome else ""
            command = "userdel %s %s" % (removehome, username)
            exitCode, stdout, stderr = j.sal.process.execute(command)

            if exitCode:
                output = "\n".join(("Stdout:", stdout, "Stderr:", stderr))
                raise j.exceptions.RuntimeError("Failed to remove user %s, error: %s" % (username, output))
            return True

    def setUnixUserPassword(self, username, password):
        """Set a password on unix user

        @param username: Name of the user to enable
        @type username: string

        @param password: Password to set on the user
        @type username: string

        """
        if not j.sal.unix.unixUserExists(username):
            raise ValueError("User [%s] does not exist, cannot set password" % username)
        else:
            command = "echo '%s:%s' | chpasswd" % (username, password)
            exitCode, stdout, stderr = j.sal.process.execute(command)

            if exitCode:
                output = "\n".join(("Stdout:", stdout, "Stderr:", stderr))
                raise j.exceptions.RuntimeError("Failed to set password on user %s, error: %s" % (username, output))
            return True

    @staticmethod
    def unixUserIsInGroup(username, groupname):
        """Checks if a given user is a member of the given group

        @param username: Username to check for
        @type username: string
        @param groupname: Group to check for
        @type groupname: string

        @returns: Whether the user is a member of the group
        @rtype: bool
        """
        try:
            return user_in_group(username, groupname)
        except KeyError:
            # Unknown user/group
            return False

    def daemonize(self, chdir="/", umask=0):
        """Daemonize a process using a double fork

        This method will fork the current process to create a daemon process.
        It will perform a double fork(2), chdir(2) to the given folder (or not
        chdir at all if the C{chdir} argument is C{None}), and set the new
        process umask(2) to the value of the C{umask} argument, or not reset
        it if this argument is -1.

        While forking, a setsid(2) call will be done to become session leader
        and detach from the controlling TTY.

        In the child process, all existing file descriptors will be closed,
        including stdin, stdout and stderr, which will be re-opened to
        /dev/null.

        The method returns a tuple<bool, number>. If the first item is True,
        the current process is the daemonized process. If it is False,
        the current process is the process which called the C{daemonize}
        method, which can most likely be closed now. The second item is the
        PID of the current process.

        @attention: Make sure you know really well what fork(2) does before using this method

        @param chdir: Path to chdir(2) to after forking. Set to None to disable chdir'ing
        @type chdir: string or None
        @param umask: Umask to set after forking. Set to -1 not to set umask
        @type umask: number

        @returns: Daemon status and PID
        @rtype: tuple<bool, number>

        @raise RuntimeError: System does not support fork(2)
        """
        # We display a warning here when threads are discovered in the current
        # process, because forking a threaded application is a pretty bad idea.
        # This is not an in-depth check, since it only checks whether any
        # threads were created using threading.Thread. On HPUX and maybe some
        # other UNIXes we could use pthread_is_multithreaded_np, but this is
        # not available on Linux at least.
        if not hasattr(os, "fork"):
            raise j.exceptions.RuntimeError("os.fork not found, daemon mode not supported on your system")

        import threading

        if threading.activeCount() > 1:
            j.errorhandler.raiseWarning("You application got running threads, this can cause issues when using fork")

        pid = os.fork()
        if pid == 0:
            # First child
            # Become session leader...
            os.setsid()

            # Double fork
            pid = os.fork()
            if pid == 0:
                # Second child
                if umask >= 0:
                    os.umask(umask)
                if chdir:
                    os.chdir(chdir)
            else:
                # First child is useless now
                os._exit(0)
        else:
            return False, os.getpid()

        # Close all FDs
        import resource

        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if maxfd == resource.RLIM_INFINITY:
            maxfd = 1024

        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()

        for fd in range(maxfd):
            try:
                os.close(fd)
            except OSError:
                pass

        # Open fd0 to /dev/null
        redirect = getattr(os, "devnull", "/dev/null")
        os.open(redirect, os.O_RDWR)

        # dup to stdout and stderr
        os.dup2(0, 1)
        os.dup2(0, 2)

        return True, os.getpid()

    def checkApplicationInstalled(self, appname):
        """
        check if app is installed,  if yes return True
        """
        result, out, err = j.sal.process.execute("which %s" % appname, die=False)
        if result == 0 and len(out) > 5:
            return True
        return False
