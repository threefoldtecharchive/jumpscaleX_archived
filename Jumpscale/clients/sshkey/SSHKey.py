from Jumpscale import j

class SSHKey(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
        @url = jumpscale.sshkey.1
        name* = "" (S)
        pubkey = "" (S)
        allow_agent = True (B)
        passphrase = "" (S)
        privkey = "" (S)
        duration = 86400 (I)
        path = "" (S)
        """

    def _init(self):
        self._agent = None

    def _init_new(self):

        self._connected = None

        if self.data.name == "":
            raise RuntimeError("need to specify name")

        if self.path=="":
            keyspath="%s/keys"%(j.sal.fs.getcwd())
            keyspath_system = j.core.tools.text_replace("{DIR_HOME}/.ssh/%s"%self.name)
            if j.sal.fs.exists(keyspath):
                # means we are in directory where keys dir is found
                self.path = keyspath
            elif j.sal.fs.exists(keyspath_system):
                self.path = keyspath

        if not self.pubkey:
            path = '%s.pub' % (self.path)
            if not j.sal.fs.exists(path):
                cmd = 'ssh-keygen -f {} -y > {}'.format(self.path, path)
                j.sal.process.execute(cmd)
            self.pubkey=j.sal.fs.readFile(path)

        if not self.privkey:
            self.privkey=j.sal.fs.readFile(self.path)

        self.save()
        self.data.autosave = True #means every write will be saved (is optional to set)

    @property
    def agent(self):

        def getagent(name):
            for item in j.clients.sshkey.sshagent.get_keys():
                if j.sal.fs.getBaseName(item.keyname) == name:
                    return item
            raise RuntimeError("Could not find agent for key with name:%s" % name)

        if self._agent is None:
            if not j.clients.sshkey.exists(self.name):
                self.load()
            self._agent = getagent(self.name)
        return self._agent


    def delete(self):
        """
        will delete from ~/.ssh dir as well as from config
        """
        self._logger.debug("delete:%s" % self.name)
        self.config.delete()
        self.delete_from_sshdir()

    def delete_from_sshdir(self):
        j.sal.fs.remove("%s.pub" % self.path)
        j.sal.fs.remove("%s" % self.path)

    def write_to_sshdir(self):
        j.sal.fs.writeFile(self.path, self.privkey)
        j.sal.fs.writeFile(self.path + ".pub", self.pubkey)

    def generate(self, reset=False):
        self._logger.debug("generate ssh key")
        if reset:
            self.delete_from_sshdir()
        else:
            if not j.sal.fs.exists(self.path):
                if self.privkey != "" and self.pubkey != "":
                    self.write_to_sshdir()

        if not j.sal.fs.exists(self.path) or reset:
            cmd = 'ssh-keygen -t rsa -f %s -q -P "%s"' % (self.path, self.passphrase)
            j.sal.process.execute(cmd, timeout=10)

        self._init_new() #will load the info from fs

    def sign_ssh_data(self, data):
        return self.agent.sign_ssh_data(data)

    def load(self, duration=3600 * 24):
        """
        load ssh key in ssh-agent, if no ssh-agent is found, new ssh-agent will be started
        """
        # self.generate()
        self._logger.debug("load sshkey: %s for duration:%s" % (self.name, duration))
        j.clients.sshkey.key_load(self.path, passphrase=self.passphrase, returnObj=False, duration=duration)

    def unload(self):
        cmd = "ssh-add -d %s " % (self.path)
        j.sal.process.executeInteractive(cmd)

    def is_loaded(self):
        """
        check if key is loaded in the ssh agent
        """
        if self.name in j.clients.sshkey.listnames():
            self._logger.debug("ssh key: %s loaded", self.name)
            return True

        self._logger.debug("ssh key: %s is not loaded", self.name)
        return False
