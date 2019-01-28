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

        self._client_ = None
        self._transport_ = None

        self._ftp = None
        self._syncer = None

    def mkdir(self,path):
        cmd = "mkdir -p %s"%path
        self.execute(cmd)

    @property
    def isprivate(self):
        if self._private is None:
            self._private = j.sal.nettools.tcpPortConnectionTest(self.addr_priv, self.port_priv, 1)
        return self._private

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

    @property
    def sshkey_obj(self):
        """
        return right sshkey
        """
        if self.sshkey_name in [None, '']:
            raise RuntimeError('sshkeyname needs to be specified')
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
        :type pubkey: str, optional
        """
        if not pubkey:
            pubkey = self.sshkey_obj.pubkey
        if not pubkey:
            raise RuntimeError('pubkey not given')
        j.builder.system.ssh.authorize(user=user, key=pubkey)

    def shell(self):
        cmd = 'ssh {login}@{addr} -p {port}'.format(**self.data._ddict)
        j.sal.process.executeWithoutPipe(cmd)

    @property
    def syncer(self):
        """
        is a tool to sync local files to your remote ssh instance
        :return:
        """
        if self._syncer is None:
            self._syncer = j.tools.syncer.get(name=self.name, sshclient_name=self.name)
        return self._syncer

    @property
    def executor(self):
        if not self._executor:
            self._executor = j.tools.executor.ssh_get(self)
        return self._executor

    def portforward_to_local(self, remoteport, localport):
        """
        forward remote port on host to the local one, so we can connect over localhost
        :param remoteport: the port to forward to local
        :param localport: the local tcp port to be used (will terminate on remote)
        :return:
        """
        self.portforwardKill(localport)
        C = "ssh -L %s:localhost:%s %s@%s -p %s" % (
            remoteport, localport, self.login, self.addr, self.port)
        print(C)
        pm = j.builder.system.processmanager.get() #need to use other one, no longer working #TODO:
        pm.ensure(cmd=C, name="ssh_%s" % localport, wait=0.5)
        print("Test tcp port to:%s" % localport)
        if not j.sal.nettools.waitConnectionTest("127.0.0.1", localport, 10):
            raise RuntimeError("Cannot open ssh forward:%s_%s_%s" %
                               (self, remoteport, localport))
        print("Connection ok")

    def portforward_kill(self, localport):
        """
        kill the forward
        :param localport:
        :return:
        """
        print("kill portforward %s" % localport)
        pm = j.builder.system.processmanager.get()
        pm.processmanager.stop('ssh_%s' % localport)


