from Jumpscale import j
JSBASE = j.application.JSBaseClass

from .ExecutorBase import ExecutorBase

import subprocess
import os
import pytoml
import socket
import sys


class ExecutorLocal(ExecutorBase):

    __jslocation__ = "j.tools.executorLocal"

    def _init(self):
        self._cache_expiration = 3600
        self.type = "local"
        self._id = 'localhost'

    def exists(self, path):
        return j.sal.fs.exists(path)



    def execute(
            self,cmd,
            die=True,
            showout=False,
            timeout=1000,
            env=None,
            sudo=False,
            replace=True):
        """
        @RETURN rc, out, err
        """
        if replace:
            if env is None:
                env={}
            env.update(self.env)
            assert self.env!={}
            cmd = self.replace(cmd,args=env)

        if sudo:
            raise RuntimeError("sudo not supported")

        # self._logger.debug(cmd)

        rc, out, err = j.sal.process.execute(cmd, die=die, showout=showout, timeout=timeout,replace=replace)

        return rc, out, err

    def executeRaw(self, cmd, die=True, showout=False):
        return self.execute(cmd, die=die, showout=showout)

    # def executeInteractive(self, cmds, die=True, checkok=None):
    #     cmds = self.commands_transform(cmds, die, checkok=checkok)
    #     return j.sal.process.executeWithoutPipe(cmds)

    def upload(self, source, dest, dest_prefix="", ignoredir=None,ignorefiles=None, recursive=True):
        """

        :param source:
        :param dest:
        :param dest_prefix:
        :param ignoredir: if None will be [".egg-info",".dist-info"]
        :param recursive:
        :param ignoredir: the following are always in, no need to specify ['.egg-info', '.dist-info', '__pycache__']
        :param ignorefiles: the following are always in, no need to specify: ["*.egg-info","*.pyc","*.bak"]
        :return:
        """
        if dest_prefix != "":
            dest = j.sal.fs.joinPaths(dest_prefix, dest)
        if j.sal.fs.isDir(source):
            j.sal.fs.copyDirTree(
                source,
                dest,
                keepsymlinks=True,
                deletefirst=False,
                overwriteFiles=True,
                ignoredir=ignoredir,
                ignorefiles=ignorefiles,
                rsync=True,
                ssh=False,
                recursive=recursive)
        else:
            j.sal.fs.copyFile(source, dest, overwriteFile=True)
        self._cache.reset()

    def download(self, source, dest, source_prefix=""):
        if source_prefix != "":
            source = j.sal.fs.joinPaths(source_prefix, source)

        if j.sal.fs.isFile(source):
            j.sal.fs.copyFile(source, dest)
        else:
            j.sal.fs.copyDirTree(
                source,
                dest,
                keepsymlinks=True,
                deletefirst=False,
                overwriteFiles=True,
                ignoredir=[
                    ".egg-info",
                    ".dist-info"],
                ignorefiles=[".egg-info"],
                rsync=True,
                ssh=False)

    def file_read(self, path):
        return j.sal.fs.readFile(path)

    def file_write(self, path, content, mode=None, owner=None,
                   group=None, append=False, sudo=False,showout=True):
        j.sal.fs.createDir(j.sal.fs.getDirName(path))
        j.sal.fs.writeFile(path, content, append=append)
        if owner is not None or group is not None:
            j.sal.fs.chown(path, owner, group)
        if mode is not None:
            j.sal.fs.chmod(path, mode)


    @property
    def state_on_system(self):
        """
        is dict of all relevant param's on system
        """
        if self._state_on_system == None:
            def getenv():
                res = {}
                for key, val in os.environ.items():
                    res[key] = val
                return res

            homedir = j.core.myenv.config["DIR_HOME"]

            # print ("INFO: stateonsystem for local")
            res = {}
            res["env"] = getenv()
            res["uname"] = subprocess.Popen("uname -mnprs", stdout=subprocess.PIPE,
                                            shell=True).stdout.read().decode().strip()
            res["hostname"] = socket.gethostname()

            if "darwin" in sys.platform.lower():
                res["os_type"] = "darwin"
            elif "linux" in sys.platform.lower():
                res["os_type"] = "ubuntu"  # dirty hack, will need to do something better, but keep fast
            else:
                print("need to fix for other types (check executorlocal")
                sys.exit(1)

            path = "%s/.profile_js" % (homedir)
            if os.path.exists(path):
                res["bashprofile"] = j.sal.fs.readFile(path)
            else:
                res["bashprofile"] = ""

            # if os.path.exists("/root/.iscontainer"):
            #     res["iscontainer"] = True
            # else:
            #     res["iscontainer"] = False

            res["HOME"] = j.core.myenv.config["DIR_HOME"]

            self._state_on_system = res

        return self._state_on_system
