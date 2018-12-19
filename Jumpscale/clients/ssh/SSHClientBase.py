from Jumpscale import j


class SSHClientBase(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
        @url = jumpscale.sshkey.1
        name* = ""
        addr = ""
        port = 22
        addr_priv = ""
        port_priv = 22
        login = ""
        passwd = ""
        sshkey = ""
        clienttype = ""
        proxy = ""
        timeout = 60
        forward_agent = true
        allow_agent = true
        stdout = true    
        """

    def _init(self):
        self.async_ = False
        self._private = None
        self._connected = None
        self._prefab = None

    @property
    def prefab(self):
        if not self._prefab:
            ex = j.tools.executor
            # executor = ex.getSSHViaProxy(self.addr_variable) if self.proxy else ex.ssh_get(self)
            executor = ex.ssh_get(self)
            if self.login != "root":
                executor.state_disabled = True
            self._prefab = executor.prefab
        return self._prefab


    @property
    def isprivate(self):
        if self._private is None:
            self._private = self.addr_priv and not j.sal.nettools.tcpPortConnectionTest(self.addr, self.port, 1)
        return self._private

    # SETTERS & GETTERS

    @property
    def addr_variable(self):
        if self.isprivate:
            return self.config.data["addr_priv"]
        else:
            return self.config.data["addr"]


    @property
    def port_variable(self):
        if self.isprivate:
            return self.config.data["port_priv"]
        else:
            return self.config.data["port"]


    # @property
    # def ssh_client_proxy(self):
    #     """
    #     ssh client to server which acts as proxy
    #     """
    #     return j.clients.ssh.get(self.proxy)


    @property
    def sshkey(self):
        """
        return right sshkey
        """
        if not self.sshkey:
            return None
        return j.clients.sshkey.get(self.sshkey)

    @property
    def isconnected(self):
        if self._connected is None:
            self._connected = j.sal.nettools.tcpPortConnectionTest(self.addr_variable, self.port_variable, 1)
            self.active = True
            self._sshclient = None
            self._ftpclient = None
        return self._connected

    def ssh_authorize(self, user, key=None, pubkey=None):
        """add key to authorized users, if key is specified will get public key from sshkey client,
        or can directly specify the public key. If both are specified key name instance will override public key.

        :param user: user to authorize
        :type user: str
        :param key: name of sshkey instance to use, defaults to None
        :param key: str, optional
        :param pubkey: public key to authorize, defaults to None
        :param pubkey: str, optional
        """
        if key:
            sshkey = j.clients.sshkey.get(key)
            pubkey = sshkey.pubkey
        if pubkey in [None,""]:
            raise RuntimeError("pubkey not given")
        self.prefab.system.ssh.authorize(user=user, key=pubkey)
