from Jumpscale import j


class SSHKey(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
        @url = jumpscale.sshkey.client
        name* = "" (S)
        pubkey = "" (S) 
        allow_agent = True (B)
        passphrase = "" (S)
        privkey = "" (S)
        duration = 86400 (I)
        path = "" (S) #path of the private key
        """

    def _init2(self, **kwargs):

        self._connected = None

        if self.name == "":
            raise RuntimeError("need to specify name")

        self.autosave = True  # means every write will be saved (is optional to set)

        if self.path != "" and j.sal.fs.exists(self.path):
            if not self.privkey:
                self.privkey = j.sal.fs.readFile(self.path)

            if not self.pubkey and self.privkey:
                path = "%s.pub" % (self.path)
                if not j.sal.fs.exists(path):
                    cmd = 'ssh-keygen -f {} -N "{}"'.format(self.path, self.passphrase)
                    j.sal.process.execute(cmd)
                self.pubkey = j.sal.fs.readFile(path)
                self.save()

    def generate(self, reset=False):
        """
        Generate ssh key

        :param reset: if True, then delete old ssh key from dir, defaults to False
        :type reset: bool, optional
        """
        self._log_debug("generate ssh key")

        if self.path == "":
            keyspath = "%s/keys" % (j.sal.fs.getcwd())
            keyspath_system = j.core.tools.text_replace("{DIR_HOME}/.ssh/%s" % self.name)
            if j.sal.fs.exists(keyspath):
                # means we are in directory where keys dir is found
                self.path = keyspath
            else:
                self.path = keyspath_system

        if reset:
            self.delete_from_sshdir()
            self.pubkey = ""
            self.privkey = ""

        else:
            if not j.sal.fs.exists(self.path):
                if self.privkey != "" and self.pubkey != "":
                    self.write_to_sshdir()

        if self.pubkey:
            raise RuntimeError("cannot generate key because pubkey already known")
        if self.privkey:
            raise RuntimeError("cannot generate key because privkey already known")

        if not j.sal.fs.exists(self.path) or reset:
            cmd = 'ssh-keygen -t rsa -f {} -N "{}"'.format(self.path, self.passphrase)
            j.sal.process.execute(cmd, timeout=10)
            self._init_pre()

    def delete(self):
        """
        will delete from from config
        """
        self._log_debug("delete:%s" % self.name)
        j.application.JSBaseConfigClass.delete(self)
        # self.delete_from_sshdir()

    def delete_from_sshdir(self):
        j.sal.fs.remove("%s.pub" % self.path)
        j.sal.fs.remove("%s" % self.path)

    def write_to_sshdir(self):
        """
        Write to ssh dir the private and public key
        """
        j.sal.fs.writeFile(self.path, self.privkey)
        j.sal.fs.writeFile(self.path + ".pub", self.pubkey)

    def sign_ssh_data(self, data):
        return self.agent.sign_ssh_data(data)
        # TODO: does not work, property needs to be implemented

    def load(self, duration=3600 * 24):
        """
        load ssh key in ssh-agent, if no ssh-agent is found, new ssh-agent will be started

        :param duration: duration, defaults to 3600*24
        :type duration: int, optional
        """
        self._log_debug("load sshkey: %s for duration:%s" % (self.name, duration))
        j.clients.sshagent.key_load(self.path, passphrase=self.passphrase, duration=duration)

    def unload(self):
        cmd = "ssh-add -d %s " % (self.path)
        j.sal.process.executeInteractive(cmd)

    def is_loaded(self):
        """
        check if key is loaded in the ssh agent

        :return: whether ssh key was loadeed in ssh agent or not
        :rtype: bool
        """
        if self.path in j.clients.sshagent.keys_list():
            self._log_debug("ssh key: %s loaded", self.name)
            return True

        self._log_debug("ssh key: %s is not loaded", self.name)
        return False

    @property
    def pubkey_only(self):
        """
        return the key only with no type e.g.ssh-rsa or email/username
        :return:
        """
        if not self.pubkey:
            raise RuntimeError("pubkey is None")
        r = self.pubkey.split(" ")
        if len(r) == 2:
            return r[1]
        elif len(r) == 3:
            return r[1]
        else:
            raise RuntimeError("format of pubkey not ok:%s" % self.pubkey)
