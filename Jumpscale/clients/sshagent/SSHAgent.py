from Jumpscale import j
from Jumpscale.core.InstallTools import Tools

import os
import sys

Tools = j.core.tools
MyEnv = j.core.myenv


class SSHAgent(j.application.JSBaseClass):

    __jslocation__ = "j.clients.sshagent"

    def _init(self):

        if MyEnv.sshagent:

            self._default_key = None

            self.ssh_socket_path = MyEnv.sshagent.ssh_socket_path
            self.available = MyEnv.sshagent.available
            self.keys_list = MyEnv.sshagent.keys_list
            self.key_names = MyEnv.sshagent.key_names
            self.key_paths = MyEnv.sshagent.key_paths
            self.key_default_name = MyEnv.sshagent.key_default
            self.profile_js_configure = MyEnv.sshagent.profile_js_configure
            self.kill = MyEnv.sshagent.kill
            self.start = MyEnv.sshagent.start

        else:
<<<<<<< HEAD
            raise RuntimeError("cannot use sshagent, maybe not initted?")
=======
            name = j.tools.console.askChoice("Which is your default sshkey to use", self.key_names)

        j.core.myenv.config["SSH_KEY_DEFAULT"] = name

        self.reset()

    def check(self):
        def get_key_list():
            """
            : get_key_list: loads ssh_key if failed:
            : 1- ssh-agent is down, start it
            : 2- socket is broken, remove it
            : 3- ssh-key is not added, add the default key in id_rsa
            """
            return_code, out, _ = j.sal.process.execute("ssh-add -L", showout=False, die=False, timeout=1)

            if return_code == 2:
                # Remove old socket if can't connect and start ssh-agent
                self.kill(socketpath=self.ssh_socket_path)
                self._start()

            if return_code == 1 and out.find("The agent has no identities") == 0:
                return_code, _, _ = j.sal.process.execute("ssh-add", showout=False, die=False, timeout=1)

            return return_code, out

        self._available = True
        if not j.sal.fs.exists(self.ssh_socket_path):
            self._available = False

        _, out = get_key_list()
        keys = [line.split() for line in out.splitlines() if len(line.split()) == 3]
        self._keys = list(map(lambda key: [key[2], " ".join(key[0:2])], keys))
        # get key_names loaded
        key_names = [j.sal.fs.getBaseName(i[0]) for i in self._keys]

        if "SSH_KEY_DEFAULT" not in j.core.myenv.config:
            j.core.myenv.config["SSH_KEY_DEFAULT"] = ""

        if j.core.myenv.config["SSH_KEY_DEFAULT"] == "" and len(key_names) == 1:
            j.core.myenv.config["SSH_KEY_DEFAULT"] = key_names[0]
            j.core.myenv.config_save()

        self._inited = True

    def reset(self):
        self._default_key = None
        self._inited = False
        self._available = None
        self._keys = []
        self.check()

    def available(self):
        """
        Check if agent available
        :return: True if agent is available, False otherwise
        :rtype: bool
        """
        self.check()
        return self._available

    def keys_list(self, key_included=False):
        """
        kosmos 'print(j.clients.sshkey.keys_list())'
        list ssh keys from the agent

        :param key_included: defaults to False
        :type key_included: bool, optional
        :raises RuntimeError: Error during listing of keys
        :return: list of paths
        :rtype: list
        """

        self.check()
        if key_included:
            return self._keys
        else:
            return [i[0] for i in self._keys]

    @property
    def key_names(self):
        self.check()
        return [j.sal.fs.getBaseName(i[0]) for i in self._keys]

    @property
    def key_paths(self):
        return [i[0] for i in self._keys]

    @property
    def key_default_or_none(self):
        """
        see if we can find the default sshkey using sshagent

        j.clients.sshagent.key_default_or_none

        :raises RuntimeError: sshkey not found in sshagent
        :raises RuntimeError: more than one sshkey is found in sshagent
        :return: j.clients.sshkey.new() ...
        :rtype: sshkey object or None
        """
        if not self._default_key:
            self.check()

            if j.core.myenv.config["SSH_KEY_DEFAULT"] == "":
                r = self.key_names
                if len(r) == 0:
                    raise RuntimeError("could not find sshkey in sshagent")
                elif len(r) > 1:
                    if j.application.interactive:
                        self.default_key_select()
                    else:
                        raise RuntimeError('default sshkey not specified in j.core.myenv.config["SSH_KEY_DEFAULT"]')
                else:
                    raise RuntimeError("bug")

            for path, key in self.keys_list(True):
                name = j.sal.fs.getBaseName(path).lower()
                if name == j.core.myenv.config["SSH_KEY_DEFAULT"]:
                    if j.sal.fs.exists(path):
                        self._default_key = j.clients.sshkey.get(name=name, pubkey=key)
                    else:
                        self._default_key = j.clients.sshkey.get(name=name, pubkey=key, path=path)

                    return self._default_key
            return None
        return self._default_key
>>>>>>> development_builder

    @property
    def key_default(self):
        """
        see if we can find the default sshkey using sshagent

        j.clients.sshagent.key_default

        :raises RuntimeError: sshkey not found in sshagent
        :raises RuntimeError: more than one sshkey is found in sshagent
        :return: j.clients.sshkey.new() ...
        :rtype: sshkey object or None
        """
        if not self._default_key:
            raise RuntimeError("not implemented yet")
            self._default_key = j.clients.sshkey.get(name=self.key_default_name, pubkey=key)
            # for path, key in self.keys_list(True):
            #     name = j.sal.fs.getBaseName(path).lower()
            #     if name == MyEnv.config["SSH_KEY_DEFAULT"]:
            #         if Tools.exists(path):
            #             self._default_key = j.clients.sshkey.get(name=self.key_default_name, pubkey=key)
            #         else:
            #             self._default_key = j.clients.sshkey.get(name=self.key_default_name, pubkey=key, path=path)
            #
            #         return self._default_key
            # return None
        return self._default_key

    def key_path_get(self, keyname="", die=True):
        """
        Returns Path of public key that is loaded in the agent

        :param keyname: name of key loaded to agent to get its path, if empty will check if there is 1 loaded, defaults to ""
        :type keyname: str, optional
        :param die:Raise error if True,else do nothing, defaults to True
        :type die: bool, optional
        :raises RuntimeError: Key not found with given keyname
        :return: path of public key
        :rtype: str
        """
        keyname = j.sal.fs.getBaseName(keyname)
        for item in self.keys_list():
            if item.endswith(keyname):
                return item
        if die:
            raise RuntimeError("Did not find key with name:%s, check its loaded in ssh-agent with ssh-add -l" % keyname)

    def key_pub_get(self, keyname=None):
        """
        Returns Content of public key that is loaded in the agent

        :param keyname: name of key loaded to agent to get content from, if not specified is default
        :type keyname: str
        :raises RuntimeError: Key not found with given keyname
        :return: Content of public key
        :rtype: str
        """
        key = self._paramiko_key_get(keyname)
        j.shell()

    def _paramiko_keys_get(self):
        import paramiko.agent

        a = paramiko.agent.Agent()
        return [key for key in a.get_keys()]

    def _paramiko_key_get(self, keyname=None):
        if not keyname:
            keyname = j.core.myenv.sshagent.key_default
        for key in self._paramiko_keys_get():
            # ISSUE, is always the same name, there is no way how to figure out which sshkey to use?
            if key.name == keyname:
                # maybe we can get this to work using comparing of the public keys?
                return key

        raise RuntimeError("could not find key:%s" % keyname)

    def sign(self, data, keyname=None, hash=True):
        """
        will sign the data with the ssh-agent loaded
        :param data: the data to sign
        :param hash, if True, will use
        :param keyname is the name of the key to use to sign, if not specified will be the default key
        :return:
        """
        if not j.data.types.bytes.check(data):
            data = data.encode()
        self._init()
        import hashlib

        key = self._paramiko_key_get(keyname)
        data_sha1 = hashlib.sha1(data).digest()
        res = key.sign_ssh_data(data_sha1)
        if hash:
            m = hashlib.sha256()
            m.update(res)
            return m.digest()
        else:
            return res

    def _start(self):
        """

        start ssh-agent, kills other agents if more than one are found

        :raises RuntimeError: Couldn't start ssh-agent
        :raises RuntimeError: ssh-agent was not started while there was no error
        :raises RuntimeError: Could not find pid items in ssh-add -l
        """

        socketpath = self.ssh_socket_path

        ssh_agents = j.sal.process.getPidsByFilter("ssh-agent")
        for pid in ssh_agents:
            p = j.sal.process.getProcessObject(pid)
            if socketpath not in p.cmdline():
                j.sal.process.kill(pid)

        if not Tools.exists(socketpath):
            j.sal.fs.createDir(j.sal.fs.getParent(socketpath))
            # ssh-agent not loaded
            self._log_info("start ssh agent")
            rc, out, err = Tools.execute("ssh-agent -a %s" % socketpath, die=False, showout=False, timeout=20)
            if rc > 0:
                raise RuntimeError("Could not start ssh-agent, \nstdout:%s\nstderr:%s\n" % (out, err))
            else:
                if not Tools.exists(socketpath):
                    err_msg = "Serious bug, ssh-agent not started while there was no error, " "should never get here"
                    raise RuntimeError(err_msg)

                # get pid from out of ssh-agent being started
                piditems = [item for item in out.split("\n") if item.find("pid") != -1]

                # print(piditems)
                if len(piditems) < 1:
                    self._log_debug("results was: %s", out)
                    raise RuntimeError("Cannot find items in ssh-add -l")

                self._init()

                pid = int(piditems[-1].split(" ")[-1].strip("; "))

                socket_path = j.sal.fs.joinPaths("/tmp", "ssh-agent-pid")
                j.sal.fs.writeFile(socket_path, str(pid))
                # self.sshagent_init()
                j.clients.sshkey._sshagent = None
                self._available = None
            return

        j.clients.sshkey._sshagent = None

<<<<<<< HEAD
=======
    def available_1key_check(self):
        """
        checks that ssh-agent is active and there is 1 key loaded
        :return:
        """
        if not self.available():
            return False
        return len(self._keys) == 1

    def kill(self, socketpath=None):
        """
        Kill all agents if more than one is found

        :param socketpath: socketpath, defaults to None
        :type socketpath: str, optional
        """
        j.sal.process.killall("ssh-agent")
        socketpath = self.ssh_socket_path if not socketpath else socketpath
        j.sal.fs.remove(socketpath)
        j.sal.fs.remove(j.sal.fs.joinPaths("/tmp", "ssh-agent-pid"))
        self._available = None
        self._inited = False
        self._log_debug("ssh-agent killed")

>>>>>>> development_builder
    def test(self):
        """
        kosmos 'j.clients.sshagent.test()'

        """

        self._log_info("sshkeys:%s" % j.clients.sshkey.listnames())
        if self.available():
            self._log_info("sshkeys:%s" % self.key_paths)

        j.clients.sshagent.kill()  # goal is to kill & make sure it get's loaded automatically
        j.clients.sshagent.start()

        # lets generate an sshkey with a passphrase
        passphrase = "12345"
        path = "/root/.ssh/test_key"
        skey = j.clients.sshkey.get(name="test", path=path, passphrase=passphrase)
        skey.save()

        # this will reload the key from the db
        skey_loaded = j.clients.sshkey.get(name="test")

        assert skey_loaded.data._ddict == skey.data._ddict

        skey.generate(reset=True)
        skey.load()

        assert skey.is_loaded()

        if not j.core.platformtype.myplatform.isMac:
            # on mac does not seem to work
            skey.unload()
            assert skey.is_loaded() is False

        path = "/root/.ssh/test_key_2"
        skey2 = j.clients.sshkey.get(name="test2", path=path)
        skey2.generate(reset=True)
        skey2.load()
        assert skey2.is_loaded()
        skey2.unload()
        assert skey2.is_loaded() is False

        assert self.available()
        self.kill()
        self.start()
        assert self.available()

        # Clean up after test
        self.kill()
        skey.delete_from_sshdir()
        skey2.delete_from_sshdir()
        skey.delete()
        skey2.delete()
