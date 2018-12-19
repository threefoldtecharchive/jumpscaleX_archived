from Jumpscale import j
JSBASE = j.application.JSBaseClass

from .ExecutorBase import *
import os


class ExecutorSSH(ExecutorBase):

    def __init__(self, sshclient, debug=False, checkok=False):
        ExecutorBase.__init__(self, debug=debug, checkok=checkok)

        self.sshclient = sshclient
        self.type = "ssh"

        self._id = None

        self.__check_base = None

    def exists(self, path):
        if path == "/env.sh":
            raise RuntimeError("SS")

        rc, _, _ = self.execute('test -e %s' % path, die=False, showout=False)
        if rc > 0:
            return False
        else:
            return True

    @property
    def id(self):
        if self._id is None:
            uid =  self.state_on_system["uid"]
            self._id = '%s-%s-%s' % (self.sshclient.addr, self.sshclient.port,uid)
        return self._id

    def executeRaw(self, cmd, die=True, showout=False):
        return self.sshclient.execute(cmd, die=die, showout=showout)

    def execute(
            self,
            cmds,
            die=True,
            checkok=False,
            showout=True,
            timeout=None,
            env={},
            asScript=True,
            sudo=False,
            shell=False,
            replace=True):
        """
        return (rc,out,err)
        """
        if replace:
            if env is None:
                env={}
            env.update(self.env)
            assert self.env!={}
            cmds = self.replace(cmds,args=env)

        # if cmds.find("cat /root/.bash_profile") != -1:
        #     raise RuntimeError("JJ")
        # if cmds.find("test -e /root/.bash_profile") != -1:
        #     raise RuntimeError("JJ")
        cmds2 = self.commands_transform(
            cmds, die, checkok=checkok, env=env, sudo=sudo)
        if cmds.find("\n") != -1 and asScript:
            if showout:
                self._logger.info(
                    "EXECUTESCRIPT} %s:%s:\n%s" %
                    (self.sshclient.addr, self.sshclient.port, cmds))
            # sshkey = self.sshclient.key_filename or ""
            return self._execute_script(
                content=cmds,
                showout=showout,
                die=die,
                checkok=checkok,
                sudo=sudo)

        if cmds.strip() == "":
            raise RuntimeError("cmds cannot be empty")

        # online command, we use prefab
        if showout:
            self._logger.info("EXECUTE %s:%s: %s" %
                             (self.sshclient.addr, self.sshclient.port, cmds))

        if sudo:
            cmds2 = self.sudo_cmd(cmds2)
        rc, out, err = self.sshclient.execute(
            cmds2, die=die, showout=showout, timeout=timeout)

        if showout:
            self._logger.debug("EXECUTE OK")

        if checkok and die:
            out = self._docheckok(cmds, out)

        return rc, out, err

    def executeRaw(self,cmds,die=True,showout=True,timeout=120):
        rc, out, err = self.sshclient.execute(cmds, die=die, showout=showout, timeout=timeout)
        return rc, out, err

    def _execute_script(
            self,
            content="",
            die=True,
            showout=True,
            checkok=None,
            sudo=False):
        """
        @param remote can be ip addr or hostname of remote,
                    if given will execute cmds there
        """

        if "sudo -H -SE" in content:
            raise RuntimeError(content)

        if showout:
            self._logger.info(
                "EXECUTESCRIPT {}:{}:\n'''\n{}\n'''\n".format(
                    self.sshclient.addr,
                    self.sshclient.port,
                    content))

        if content[-1] != "\n":
            content += "\n"

        if die:
            content = "set -ex\n{}".format(content)

        if sudo:
            login = self.sshclient.config.data['login']
            path = "/tmp/tmp_prefab_removeme_{}.sh".format(login)
        else:
            path = "/tmp/prefab_{}.sh".format(
                j.data.idgenerator.generateRandomInt(1, 100000))

        j.sal.fs.writeFile(path, content)

        # just in case of the same machine.
        path2 = "/tmp/prefab_{}.sh".format(
            j.data.idgenerator.generateRandomInt(1, 100000))
        self.sshclient.copy_file(path, path2)  # is now always on tmp
        if sudo and "LEDE" not in j.core.platformtype.get(self).osname:
            passwd = self.sshclient.config.data['passwd_']
            cmd = 'echo \'{}\' | sudo -H -SE -p \'\' bash "{}"'.format(
                passwd, path2)
        else:
            cmd = "bash {}".format(path2)
        rc, out, err = self.sshclient.execute(cmd, die=die, showout=showout)

        if checkok and die:
            out = self._docheckok(content, out)

        j.sal.fs.remove(path)
        self.sshclient.sftp.unlink(path2)
        return rc, out, err

    def _check_base(self):
        if not self.__check_base:
            def do():
                #means we did not check it
                C="""
                echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted > /etc/apt/sources.list
                apt update
                apt install rsync curl wget -y
                apt install git -y
                """
                self.execute(j.core.text.strip(C))
                return "OK"

            self.cache.get("_check_base", method=do, expire=3600*24, refresh=False, retry=2, die=True)

            self.__check_base = True

    def upload(self, source, dest, dest_prefix="", recursive=True,
               createdir=True,
               rsyncdelete=True,
               ignoredir=None,
               ignorefiles=None,
               keepsymlinks=True):
        """

        :param source:
        :param dest:
        :param dest_prefix:
        :param recursive:
        :param createdir:
        :param rsyncdelete:
        :param ignoredir: the following are always in, no need to specify ['.egg-info', '.dist-info', '__pycache__']
        :param ignorefiles: the following are always in, no need to specify: ["*.egg-info","*.pyc","*.bak"]
        :param keepsymlinks:
        :param showout:
        :return:
        """

        if dest_prefix != "":
            dest = j.sal.fs.joinPaths(dest_prefix, dest)
        if dest[0] != "/":
            raise j.exceptions.RuntimeError("need / in beginning of dest path")
        if source[-1] != "/":
            source += ("/")
        if dest[-1] != "/":
            dest += ("/")
        dest = "root@%s:%s" % (self.sshclient.addr, dest)
        self._check_base()
        j.sal.fs.copyDirTree(
            source,
            dest,
            keepsymlinks=keepsymlinks,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=ignoredir,
            ignorefiles=ignorefiles,
            rsync=True,
            ssh=True,
            sshport=self.sshclient.port,
            recursive=recursive,
            createdir=createdir,
            rsyncdelete=rsyncdelete)
        self._cache.reset()

    def download(self, source, dest, source_prefix="",
               ignoredir=None,
               ignorefiles=None,
               recursive=True):
        """

        :param source:
        :param dest:
        :param source_prefix:
        :param recursive:
        :param ignoredir: the following are always in, no need to specify ['.egg-info', '.dist-info', '__pycache__']
        :param ignorefiles: the following are always in, no need to specify: ["*.egg-info","*.pyc","*.bak"]
        :return:
        """
        self._check_base()
        if source_prefix != "":
            source = j.sal.fs.joinPaths(source_prefix, source)
        if source[0] != "/":
            raise j.exceptions.RuntimeError(
                "need / in beginning of source path")
        source = "root@%s:%s" % (self.sshclient.addr, source)
        j.sal.fs.copyDirTree(
            source,
            dest,
            keepsymlinks=True,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=ignoredir,
            ignorefiles=ignorefiles,
            rsync=True,
            ssh=True,
            sshport=self.sshclient.port,
            recursive=recursive)

    def __repr__(self):
        return ("Executor ssh: %s (%s)" %
                (self.sshclient.addr, self.sshclient.port))

    __str__ = __repr__
