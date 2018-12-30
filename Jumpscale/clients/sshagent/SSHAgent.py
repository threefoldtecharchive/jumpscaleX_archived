from Jumpscale import j
from Jumpscale.core.InstallTools import Tools

import os


class SSHAgent(j.application.JSBaseConfigClass):
    _SCHEMATEXT = """
    @url = jumpscale.sshagent.client
    name* = "" (S)
    passphrase = "" (S)
    path = "" (S)
    """

    @property
    def keyname_default(self):
        """
        see if we can find the default sshkey in sshagent
        :return:
        """
        r = [j.sal.fs.getBaseName(item) for item in self.keys_list()]
        if len(r) == 0:
            raise RuntimeError("could not find sshkey in sshagent")
        if len(r) > 1:
            raise RuntimeError("found more than 1 sshkey in sshagent")
        return r[0]

    def key_load(self, duration=3600 * 24):
        """
        load the key on path

        """
        if not j.sal.fs.exists(self.path):
            raise RuntimeError(
                "Cannot find path:%sfor sshkey (private key)" % self.path)

        self.check()

        name = j.sal.fs.getBaseName(self.path)

        if name in [j.sal.fs.getBaseName(item) for item in self.keys_list()]:
            return

        # otherwise the expect script will fail
        path0 = j.sal.fs.pathNormalize(self.path)

        self._logger.info("load ssh key: %s" % path0)
        j.sal.fs.chmod(self.path, 0o600)
        if self.passphrase:
            self._logger.debug("load with passphrase")
            C = """
                echo "exec cat" > ap-cat.sh
                chmod a+x ap-cat.sh
                export DISPLAY=1
                echo {self.passphrase} | SSH_ASKPASS=./ap-cat.sh ssh-add -t {duration} {self.path}
                """.format(path=path0, passphrase=self.passphrase, duration=duration)
            try:
                j.sal.process.execute(C, showout=False)
            finally:
                j.sal.fs.remove("ap-cat.sh")
        else:
            # load without passphrase
            cmd = "ssh-add -t %s %s " % (duration, path0)
            j.sal.process.execute(cmd)

        self._sshagent = None  # to make sure it gets loaded again

        data = {}
        data["path"] = self.path

        return self.get(instance=name, data=data)

    def profile_js_configure(self):
        '''
        js_shell 'j.clients.sshkey.profile_js_configure()'
        '''

        bashprofile_path = os.path.expanduser("~/.profile_js")
        if not j.sal.fs.exists(bashprofile_path):
            j.sal.process.execute('touch %s' % bashprofile_path)

        content = j.sal.fs.readFile(bashprofile_path)
        out = ""
        for line in content.split("\n"):
            if line.find("#JSSSHAGENT") != -1:
                continue
            if line.find("SSH_AUTH_SOCK") != -1:
                continue

            out += "%s\n" % line

        out += "export SSH_AUTH_SOCK=%s" % self.ssh_socket_path
        out = out.replace("\n\n\n", "\n\n")
        out = out.replace("\n\n\n", "\n\n")
        j.sal.fs.writeFile(bashprofile_path, out)

    def _init_ssh_env(self, force=True):
        if force or "SSH_AUTH_SOCK" not in os.environ:
            os.putenv("SSH_AUTH_SOCK", self.ssh_socket_path)
            os.environ["SSH_AUTH_SOCK"] = self.ssh_socket_path

    @property
    def ssh_socket_path(self):

        if "SSH_AUTH_SOCK" in os.environ:
            return(os.environ["SSH_AUTH_SOCK"])

        socketpath = Tools.text_replace("{DIR_VAR}/sshagent_socket")
        os.environ['SSH_AUTH_SOCK'] = socketpath
        return socketpath

    def sshagent_start(self):
        j.sal.process.execute(
            'ssh-agent -a {}'.format(os.environ['SSH_AUTH_SOCK']), showout=False, die=True, timeout=1)

    def check(self):
        """
        will check that agent started if not will start it.
        """
        if "SSH_AUTH_SOCK" not in os.environ:
            self._init_ssh_env()
            # self.sshagent_init()
        if not self.available():
            self._logger.info('Will start agent')
            self.sshagent_start()

    def key_path_get(self, keyname="", die=True):
        """
        Returns Path of public key that is loaded in the agent
        @param keyname: name of key loaded to agent to get its path, if empty will check if there is 1 loaded
        """
        keyname = j.sal.fs.getBaseName(keyname)
        for item in self.keys_list():
            if item.endswith(keyname):
                return item
        if die:
            raise RuntimeError(
                "Did not find key with name:%s, check its loaded in ssh-agent with ssh-add -l" %
                keyname)

    def key_pub_get(self, keyname, die=True):
        """
        Returns Content of public key that is loaded in the agent
        @param keyname: name of key loaded to agent to get content from
        """
        keyname = j.sal.fs.getBaseName(keyname)
        for name, pubkey in self.keys_list(True):
            if name.endswith(keyname):
                return pubkey
        if die:
            raise RuntimeError(
                "Did not find key with name:%s, check its loaded in ssh-agent with ssh-add -l" %
                keyname)

    def keys_list(self, key_included=False):
        """

        js_shell 'print(j.clients.sshkey.keys_list())'

        list ssh keys from the agent
        :param key_included:
        :return: list of paths
        """
        # check if we can get keys, if not try to load the ssh-agent (need to check on linux)

        if "SSH_AUTH_SOCK" not in os.environ:
            self._init_ssh_env()
        self.check()
        cmd = "ssh-add -L"
        return_code, out, err = j.sal.process.execute(
            cmd, showout=False, die=False, timeout=1)
        if return_code:
            if return_code == 1 and out.find("The agent has no identities") != -1:
                return []
            raise RuntimeError("error during listing of keys :%s" % err)
        keys = [line.split()
                for line in out.splitlines() if len(line.split()) == 3]
        if key_included:
            return list(map(lambda key: [key[2], ' '.join(key[0:2])], keys))
        else:
            return list(map(lambda key: key[2], keys))

    def start(self):
        """
        start ssh-agent, kills other agents if more than one are found
        """
        socketpath = self.ssh_socket_path

        ssh_agents = j.sal.process.getPidsByFilter('ssh-agent')
        for pid in ssh_agents:
            p = j.sal.process.getProcessObject(pid)
            if socketpath not in p.cmdline():
                j.sal.process.kill(pid)

        if not j.sal.fs.exists(socketpath):
            j.sal.fs.createDir(j.sal.fs.getParent(socketpath))
            # ssh-agent not loaded
            self._logger.info("load ssh agent")
            rc, out, err = j.sal.process.execute("ssh-agent -a %s" % socketpath,
                                                 die=False,
                                                 showout=False,
                                                 timeout=20)
            if rc > 0:
                raise RuntimeError(
                    "Could not start ssh-agent, \nstdout:%s\nstderr:%s\n" % (out, err))
            else:
                if not j.sal.fs.exists(socketpath):
                    err_msg = "Serious bug, ssh-agent not started while there was no error, "\
                              "should never get here"
                    raise RuntimeError(err_msg)

                # get pid from out of ssh-agent being started
                piditems = [item for item in out.split(
                    "\n") if item.find("pid") != -1]

                # print(piditems)
                if len(piditems) < 1:
                    self._logger.debug("results was: %s", out)
                    raise RuntimeError("Cannot find items in ssh-add -l")

                self._init_ssh_env()

                pid = int(piditems[-1].split(" ")[-1].strip("; "))

                socket_path = j.sal.fs.joinPaths("/tmp", "ssh-agent-pid")
                j.sal.fs.writeFile(socket_path, str(pid))
                # self.sshagent_init()
                j.clients.sshkey._sshagent = None
            return

        # ssh agent should be loaded because ssh-agent socket has been
        # found
        if os.environ.get("SSH_AUTH_SOCK") != socketpath:
            self._init_ssh_env()

        j.clients.sshkey._sshagent = None

    def available(self):
        """
        Check if agent available
        :return: bool
        """
        socket_path = self.ssh_socket_path
        if not j.sal.fs.exists(socket_path):
            return False
        if "SSH_AUTH_SOCK" not in os.environ:
            self._init_ssh_env()
        return_code, out, _ = j.sal.process.execute("ssh-add -l",
                                                    showout=False,
                                                    die=False, useShell=False)
        if 'The agent has no identities.' in out:
            return True

        if return_code != 0:
            # Remove old socket if can't connect
            if j.sal.fs.exists(socket_path):
                j.sal.fs.remove(socket_path)
            return False
        else:
            return True

    def kill(self, socketpath=None):
        """
        Kill all agents if more than one is found
        :param socketpath: socketpath
        """
        j.sal.process.killall("ssh-agent")
        socketpath = self.ssh_socket_path if not socketpath else socketpath
        j.sal.fs.remove(socketpath)
        j.sal.fs.remove(j.sal.fs.joinPaths('/tmp', "ssh-agent-pid"))
        self._logger.debug("ssh-agent killed")

    def test(self):
        """
        js_shell 'j.clients.sshkey.test()'

        """

        # TODO:1 broken

        # self._logger_enable()
        self._logger.info("sshkeys:%s" % j.clients.sshkey.listnames())

        self.sshagent_kill()  # goal is to kill & make sure it get's loaded automatically

        # lets generate an sshkey with a passphrase
        skey = self.SSHKey(name="test")
        skey.passphrase = "12345"
        skey.path = "apath"
        skey.save()

        # this will reload the key from the db
        skey2 = self.SSHKey(name="test")

        assert skey2._ddict == skey.data._ddict

        skey.generate(reset=True)
        skey.load()

        assert skey.is_loaded()

        if not j.core.platformtype.myplatform.isMac:
            # on mac does not seem to work
            skey.unload()
            assert skey.is_loaded() is False

        skey = self.SSHKey(name="test2")
        skey.generate()
        skey.load()
        assert skey.is_loaded()
        skey.unload()
        assert skey.is_loaded() is False

        assert self.available()
        self.sshagent_kill()
        assert self.available() is False

        self.sshagent_start()
        assert self.available()
