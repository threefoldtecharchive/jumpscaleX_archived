from Jumpscale import j
from Jumpscale.core.InstallTools import Tools

import os
import sys

class SSHAgent(j.application.JSBaseClass):

    __jslocation__ = "j.clients.sshagent"

    def _init(self):
        self._inited = False
        self._default_key = None

    @property
    def ssh_socket_path(self):

        if "SSH_AUTH_SOCK" in os.environ:
            return(os.environ["SSH_AUTH_SOCK"])

        socketpath = Tools.text_replace("{DIR_VAR}/sshagent_socket")
        os.environ['SSH_AUTH_SOCK'] = socketpath
        return socketpath



    def default_key_select(self):
        """

        kosmos 'j.clients.sshagent.default_key_select()'

        will give you a dropdown to choose from
        its to choose the default sshkey and if needed sshagent will be loaded
        :return:
        """
        self.check()
        if len(self.key_names)==1:
            j.tools.console.askYesNo("Ok to use key: '%s' as your default key?"%self.key_names[0])
            name = self.key_names[0]
        elif len(self.key_names)==0:
            print("Cannot find a possible ssh-key, please load your possible keys in your ssh-agent")
            sys.exit(1)
        else:
            name = j.tools.console.askChoice("Which is your default sshkey to use",self.key_names)

        j.core.myenv.config["SSH_KEY_DEFAULT"] = name

        self.reset()


    def check(self):

        def get_key_list():
            return_code, out, err = j.sal.process.execute("ssh-add -L", showout=False, die=False, timeout=1)
            if return_code:
                if return_code == 1 and out.find("The agent has no identities") != -1:
                    return 0,""
                else:
                    # Remove old socket if can't connect
                    if j.sal.fs.exists(self.ssh_socket_path):
                        j.sal.fs.remove(self.ssh_socket_path)
                        return get_key_list()
            return return_code, out

        if self._inited is False:
            self._available = True
            if not j.sal.fs.exists(self.ssh_socket_path):
                self._available = False

            return_code, out = get_key_list()
            if return_code:
                self._start()
            #only try once
            return_code, out = get_key_list()

            keys = [line.split() for line in out.splitlines() if len(line.split()) == 3]
            self._keys = list(map(lambda key: [key[2], ' '.join(key[0:2])], keys))

            if "SSH_KEY_DEFAULT" not in j.core.myenv.config:
                j.core.myenv.config["SSH_KEY_DEFAULT"] = ""

            if j.core.myenv.config["SSH_KEY_DEFAULT"] == "" and len(self.key_names)==1:
                j.core.myenv.config["SSH_KEY_DEFAULT"] = self.key_names[0]
                j.core.myenv.config_save()

            self._inited = True

    def reset(self):
        self._default_key = None
        self._inited = False
        self._available=None
        self._keys = []
        self.check()
        
        
    def available(self):
        '''
        Check if agent available
        :return: True if agent is available, False otherwise
        :rtype: bool
        '''
        self.check()
        return self._available

    def keys_list(self, key_included=False):
        '''
        js_shell 'print(j.clients.sshkey.keys_list())'
        list ssh keys from the agent

        :param key_included: defaults to False
        :type key_included: bool, optional
        :raises RuntimeError: Error during listing of keys
        :return: list of paths
        :rtype: list
        '''

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
        '''
        see if we can find the default sshkey using sshagent

        j.clients.sshagent.key_default_or_none

        :raises RuntimeError: sshkey not found in sshagent
        :raises RuntimeError: more than one sshkey is found in sshagent
        :return: j.clients.sshkey.new() ...
        :rtype: sshkey object or None
        '''
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
                        raise RuntimeError("default sshkey not specified in j.core.myenv.config[\"SSH_KEY_DEFAULT\"]")
                else:
                    raise RuntimeError("bug")

            for path,key in self.keys_list(True):
                name = j.sal.fs.getBaseName(path).lower()
                if name == j.core.myenv.config["SSH_KEY_DEFAULT"]:
                    if j.sal.fs.exists(path):
                        self._default_key = j.clients.sshkey.get(name=name,pubkey=key)
                    else:
                        self._default_key = j.clients.sshkey.get(name=name,pubkey=key,path=path)

                    return self._default_key
            return None
        return self._default_key

    @property
    def key_default(self):
        '''
        see if we can find the default sshkey using sshagent

        j.clients.sshagent.key_default

        :raises RuntimeError: sshkey not found in sshagent
        :raises RuntimeError: more than one sshkey is found in sshagent
        :return: j.clients.sshkey.new() ...
        :rtype: sshkey object or error
        '''

        r = self.key_default_or_none
        if r is None:
            raise RuntimeError("Could not define key_default")
        return r


        return self._default_key

    def key_load(self,path="",passphrase="", duration=3600 * 24):
        '''
        load the key on path

        :param path: path for ssh-key
        :type path: str
        :param passphrase: passphrase for ssh-key, defaults to ""
        :type passphrase: str
        :param duration: duration, defaults to 3600*24
        :type duration: int, optional
        :raises RuntimeError: Path to load sshkey on couldn't be found
        :return: sshAgent instance
        :rtype: SSHAgent
        '''
        if not j.sal.fs.exists(path):
            raise RuntimeError("Cannot find path:%sfor sshkey (private key)" % path)

        self.check()

        name = j.sal.fs.getBaseName(path)

        if name in [j.sal.fs.getBaseName(item) for item in self.keys_list()]:
            return

        # otherwise the expect script will fail
        path0 = j.sal.fs.pathNormalize(path)

        self._log_info("load ssh key: %s" % path0)
        j.sal.fs.chmod(path, 0o600)
        if passphrase:
            self._log_debug("load with passphrase")
            C = """
                echo "exec cat" > ap-cat.sh
                chmod a+x ap-cat.sh
                export DISPLAY=1
                echo {passphrase} | SSH_ASKPASS=./ap-cat.sh ssh-add -t {duration} {path}
                """.format(path=path0, passphrase=passphrase, duration=duration)
            try:
                j.sal.process.execute(C, showout=False)
            finally:
                j.sal.fs.remove("ap-cat.sh")
        else:
            # load without passphrase
            cmd = "ssh-add -t %s %s " % (duration, path0)
            j.sal.process.execute(cmd)

        self._sshagent = None  # to make sure it gets loaded again


        return self

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


    def key_path_get(self, keyname="", die=True):
        '''
        Returns Path of public key that is loaded in the agent

        :param keyname: name of key loaded to agent to get its path, if empty will check if there is 1 loaded, defaults to ""
        :type keyname: str, optional
        :param die:Raise error if True,else do nothing, defaults to True
        :type die: bool, optional
        :raises RuntimeError: Key not found with given keyname
        :return: path of public key
        :rtype: str
        '''
        keyname = j.sal.fs.getBaseName(keyname)
        for item in self.keys_list():
            if item.endswith(keyname):
                return item
        if die:
            raise RuntimeError(
                "Did not find key with name:%s, check its loaded in ssh-agent with ssh-add -l" %
                keyname)

    def key_pub_get(self, keyname, die=True):
        '''
        Returns Content of public key that is loaded in the agent

        :param keyname: name of key loaded to agent to get content from
        :type keyname: str
        :param die: Raise error if True,else do nothing, defaults to True
        :type die: bool, optional
        :raises RuntimeError: Key not found with given keyname
        :return: Content of public key
        :rtype: str
        '''
        keyname = j.sal.fs.getBaseName(keyname)
        for name, pubkey in self.keys_list(True):
            if name.endswith(keyname):
                return pubkey
        if die:
            raise RuntimeError(
                "Did not find key with name:%s, check its loaded in ssh-agent with ssh-add -l" %
                keyname)


    def _paramiko_keys_get(self):
        import paramiko.agent
        a = paramiko.agent.Agent()
        return [key for key in a.get_keys()]

    def sign(self,data,hash=True):
        """
        will sign the data with the ssh-agent loaded
        :param data: the data to sign
        :param hash, if True, will use
        :return:
        """
        if not j.data.types.bytes.check(data):
            data = data.encode()
        self.check()
        assert self.available_1key_check() == True
        import hashlib
        data_sha1 = hashlib.sha1(data).digest()
        key = self._paramiko_keys_get()[0]
        res = key.sign_ssh_data(data_sha1)
        if hash:
            m = hashlib.sha256()
            m.update(res)
            return m.digest()
        else:
            return res

    def start(self):
        '''

        kosmos 'j.clients.sshagent.start()'

        start ssh-agent, kills other agents if more than one are found

        :raises RuntimeError: Couldn't start ssh-agent
        :raises RuntimeError: ssh-agent was not started while there was no error
        :raises RuntimeError: Could not find pid items in ssh-add -l
        '''

        # ssh agent should be loaded because ssh-agent socket has been
        # found
        self.check()


    def _start(self):
        '''

        start ssh-agent, kills other agents if more than one are found

        :raises RuntimeError: Couldn't start ssh-agent
        :raises RuntimeError: ssh-agent was not started while there was no error
        :raises RuntimeError: Could not find pid items in ssh-add -l
        '''



        socketpath = self.ssh_socket_path

        ssh_agents = j.sal.process.getPidsByFilter('ssh-agent')
        for pid in ssh_agents:
            p = j.sal.process.getProcessObject(pid)
            if socketpath not in p.cmdline():
                j.sal.process.kill(pid)

        if not j.sal.fs.exists(socketpath):
            j.sal.fs.createDir(j.sal.fs.getParent(socketpath))
            # ssh-agent not loaded
            self._log_info("load ssh agent")
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
                    self._log_debug("results was: %s", out)
                    raise RuntimeError("Cannot find items in ssh-add -l")

                self.check()

                pid = int(piditems[-1].split(" ")[-1].strip("; "))

                socket_path = j.sal.fs.joinPaths("/tmp", "ssh-agent-pid")
                j.sal.fs.writeFile(socket_path, str(pid))
                # self.sshagent_init()
                j.clients.sshkey._sshagent = None
                self._available = None
            return


        j.clients.sshkey._sshagent = None

    def available_1key_check(self):
        """
        checks that ssh-agent is active and there is 1 key loaded
        :return:
        """
        if not self.available():
            return False
        return len(self.keys_list())==1

    def kill(self, socketpath=None):
        '''
        Kill all agents if more than one is found

        :param socketpath: socketpath, defaults to None
        :type socketpath: str, optional
        '''
        j.sal.process.killall("ssh-agent")
        socketpath = self.ssh_socket_path if not socketpath else socketpath
        j.sal.fs.remove(socketpath)
        j.sal.fs.remove(j.sal.fs.joinPaths('/tmp', "ssh-agent-pid"))
        self._available = None
        self._log_debug("ssh-agent killed")

    def test(self):
        """
        kosmos 'j.clients.sshagent.test()'

        """

        # self._log_info("sshkeys:%s" % j.clients.sshkey.listnames())
        if self.available():
            self._log_info("sshkeys:%s" % self.key_paths)

        j.clients.sshagent.kill()  # goal is to kill & make sure it get's loaded automatically
        j.clients.sshagent.start()

        # lets generate an sshkey with a passphrase
        passphrase = "12345"
        path = "/root/.ssh/test_key"
        skey = j.clients.sshkey.get(name="test", path=path,passphrase=passphrase)
        skey.save()

        # this will reload the key from the db
        skey_loaded =  j.clients.sshkey.get(name="test")

        assert skey_loaded.data._ddict == skey.data._ddict

        skey.generate(reset=True)
        skey.load()

        assert skey.is_loaded()

        if not j.core.platformtype.myplatform.isMac:
            # on mac does not seem to work
            skey.unload()
            assert skey.is_loaded() is False

        path="/root/.ssh/test_key_2"
        skey2 = j.clients.sshkey.get(name="test2", path=path)
        skey2.generate()
        skey2.load()
        assert skey2.is_loaded()
        skey2.unload()
        assert skey2.is_loaded() is False

        assert self.available()
        self.kill()
        assert self.available() is False

        self.sshagent_start()
        assert self.available()
        # Clean up after test
        self.kill()
        assert self.available() is False
        skey.delete_from_sshdir()
        skey2.delete_from_sshdir()
        skey.delete()
        skey2.delete()
