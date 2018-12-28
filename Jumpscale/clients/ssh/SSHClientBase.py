from Jumpscale import j


class SSHClientBase(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
        @url = jumpscale.sshkey.1
        name* = ""
        addr = ""
        port = 22
        addr_priv = ""
        port_priv = 22
        login = "root"
        passwd = ""
        sshkey_name = ""
        clienttype = ""
        proxy = ""
        timeout = 60
        forward_agent = True (B)
        allow_agent = True (B)
        stdout = true    
        """

    def _init(self):
        self.async_ = False
        self._private = None
        self._connected = None
        self._prefab = None


    @property
    def isprivate(self):
        if self._private is None:
             self._private = j.sal.nettools.tcpPortConnectionTest(self.addr_priv, self.port_priv, 1)
        return self._private

    # SETTERS & GETTERS

    @property
    def addr_variable(self):
        if self.isprivate:
            return self.addr_priv
        else:
            return self.addr


    @property
    def port_variable(self):
        if self.isprivate:
            return self.port_priv
        else:
            return self.port


    # @property
    # def ssh_client_proxy(self):
    #     """
    #     ssh client to server which acts as proxy
    #     """
    #     return j.clients.ssh.get(self.proxy)


    @property
    def sshkey_obj(self):
        """
        return right sshkey
        """
        if self.sshkey_name in [None,""]:
            raise RuntimeError("sshkeyname needs to be specified")
        return j.clients.sshkey.get(name=self.sshkey_name)

    @property
    def isconnected(self):
        if self._connected is None:
            self._connected = j.sal.nettools.tcpPortConnectionTest(self.addr_variable, self.port_variable, 1)
            self.active = True
            self._sshclient = None
            self._ftpclient = None
        return self._connected

    def ssh_authorize(self, user, pubkey=None):
        """add key to authorized users, if key is specified will get public key from sshkey client,
        or can directly specify the public key. If both are specified key name instance will override public key.

        :param user: user to authorize
        :type user: str
        :param pubkey: public key to authorize, defaults to None
        :param pubkey: str, optional
        """
        if not pubkey:
            pubkey = self.sshkey_obj.pubkey
        if pubkey in [None,""]:
            raise RuntimeError("pubkey not given")
        j.shell()
        self.prefab.system.ssh.authorize(user=user, key=pubkey)

    def shell(self):
        cmd="ssh {login}@{addr} -p {port}".format(**self.data._ddict)
        j.sal.process.executeWithoutPipe(cmd)

    @property
    def syncer(self):
        """
        is a tool to sync local files to your remote ssh instance
        :return:
        """
        if self._syncer == None:
            self._syncer = j.tools.syncer.get(name=self.name, sshclient_name=self.name)
        return self._syncer
