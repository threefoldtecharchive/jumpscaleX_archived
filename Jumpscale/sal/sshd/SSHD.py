from Jumpscale import j

OP_ADD = '+'
OP_DEL = '-'
OP_ERS = '--'


# TODO: add to JSExceptions Factory
#class SSHError(Exception, JSBASE):
#    def __init__(self):
#        JSBASE.__init__(self)


class SSHD:

    __jslocation__ = "j.sal.sshd"

    def __init__(self):
        self._local = j.tools.executorLocal
        self._keys = None
        self._transactions = []

    @property
    def SSH_ROOT(self):
        return j.tools.path.get(j.dirs.HOMEDIR).joinpath(".ssh")

    @property
    def SSH_AUTHORIZED_KEYS(self):
        return j.tools.path.get(self.SSH_ROOT).joinpath('authorized_keys')

    @property
    def keys(self):
        if self._keys is None:
            self.SSH_ROOT.makedirs_p()
            if self.SSH_AUTHORIZED_KEYS.exists():
                self._keys = self.SSH_AUTHORIZED_KEYS.text().splitlines()
                self._keys = list(filter(None, self._keys))
            else:
                self._keys = []

        return self._keys

    def addKey(self, key):
        """ Add pubkey to authorized_keys
        """
        self._transactions.append( (OP_ADD, key.strip()))

    def deleteKey(self, key):
        """ Delete pubkey from authorized_keys
        """
        self._transactions.append( (OP_DEL, key.strip()))

    def erase(self):
        """ Erase all keys from authorized_keys
        """
        self._transactions.append( (OP_ERS, None))

    def commit(self):
        """ Apply all pending changes to authorized_keys
        """
        keys = set(self.keys)
        while self._transactions:
            op, key = self._transactions.pop(0)
            if op == OP_ERS:
                keys = set()
            elif op == OP_ADD:
                keys.add(key)
            elif op == OP_DEL:
                keys.discard(key)

            self.SSH_AUTHORIZED_KEYS.write_text('\n'.join(keys))

        # force reload on next access.
        self._keys = None

    def disableNonKeyAccess(self):
        """ Disable passowrd login to server. This action doens't require
            calling to commit and applies immediately. So if you added your key
            make sure to commit it before you call this method.

            XXX this is not a smart way to do this: there could be
            entries "PasswordAuthentication yes" already in the file
        """

        pth = j.tools.path.get('/etc/ssh/sshd_config')
        pth.write_text('PasswordAuthentication no', append=True)

        self._local.execute('service ssh restart')

    # Useless in local execution
    # def secure(self, sshkeypath="", recoverypasswd=""):
    #     """
    #     * actions
    #         * will set recovery passwd for user recovery
    #         * will create a recovery user account
    #         * will disable all other users to use ssh (so only user 'recovery' can login & do self.sudo -s)
    #         * will authorize key identified with sshkeypath
    #         * will do some tricks to secure sshdaemon e.g. no pam, no root access.
    #     * locked down server where only the specified key can access and through the recovery created user

    #     @param sshkeypath if =="" then will not set the ssh keys only work with recovery passwd

    #     """
    #     def checkkeyavailable(sshkeypub):
    #         errormsg = "Could not find SSH agent, please start by 'eval \"$(ssh-agent -s)\"' before self.running this cmd,\nand make sure appropriate keys are added with ssh-add ..."
    #         sshkeypubcontent = sshkeypub.rsplit(' ', maxsplit=1)[0]
    #         # check if current priv key is in ssh-agent
    #         local = j.tools.executorLocal
    #         pids = j.sal.process.getPidsByFilter('ssh-agent')
    #         if not pids:
    #             j.events.opserror_critical(errormsg)

    #         rc, keys = local.execute('ssh-add -L')
    #         if keys == 'The agent has no identities.':
    #             j.events.opserror_critical(errormsg)

    #         for key in keys.splitlines():
    #             key, path = key.rsplit(maxsplit=1)
    #             if key == sshkeypubcontent:
    #                 return True
    #         return False

    #     if sshkeypath != "" and not j.tools.path.get(sshkeypath).exists():
    #         j.events.opserror_critical("Cannot find key on %s" % sshkeypath)

    #     if recoverypasswd == "" and "recoverypasswd" in os.environ:
    #         recoverypasswd = os.environ["recoverypasswd"]

    #     if len(recoverypasswd) < 6:
    #         j.events.opserror_critical(
    #             "Choose longer passwd (min 6), do this by doing 'export recoverypasswd=something' before self.running this script.")

    #     if sshkeypath != "":
    #         sshkeypub = j.tools.path.get(sshkeypath).joinpath(".pub").text()

    #     if sshkeypath != "" and not checkkeyavailable(sshkeypub):
    #         # add the new key
    #         self._local.execute("ssh-add %s" % sshkeypath)

    #     # make sure recovery user exists
    #     recoverypath = j.tools.path.get("/home/recovery")
    #     if recoverypath.exists():
    #         recoverypath.rmtree_p()
    #         self._local.execute("userdel recovery")

    #     self._local.execute("useradd recovery -p %s" % recoverypasswd)

    #     print("change passwd")
    #     self.changePasswd(recoverypasswd)
    #     print("ok")

    #     print("test ssh connection only using the recovery user: login/passwd combination")
    #     ssh = paramiko.SSHClient()
    #     hostname = self.connection.host().split(":")[0]
    #     port = int(self.connection.host().split(":")[1])
    #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     ssh.connect(hostname, port=port, username="recovery", password=recoverypasswd,
    #                 pkey=None, key_filename=None, timeout=None, allow_agent=False, look_for_keys=False)
    #     ssh.close()
    #     print("ssh recovery user ok")

    #     if sshkeypath != "":
    #         sshpath = j.tools.path.get("/root/.ssh")
    #         sshpath.rmtree_p()
    #         sshpath.makedirs_p("/root/.ssh")

    #         self.connection.ssh_authorize("root", sshkeypub)

    #         print("test ssh connection with pkey")
    #         ssh = paramiko.SSHClient()
    #         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #     CMDS = """
    #         #make sure user is in self.sudo group
    #         usermod -a -G self.sudo recovery

    #         #sed -i -e '/texttofind/ s/texttoreplace/newvalue/' /path/to/file
    #         sed -i -e '/.*PermitRootLogin.*/ s/.*/PermitRootLogin without-password/' /etc/ssh/sshd_config
    #         sed -i -e '/.*UsePAM.*/ s/.*/UsePAM no/' /etc/ssh/sshd_config
    #         sed -i -e '/.*Protocol.*/ s/.*/Protocol 2/' /etc/ssh/sshd_config

    #         #only allow root & recovery user (make sure it exists)
    #         sed -i -e '/.*AllowUsers.*/d' /etc/ssh/sshd_config
    #         echo 'AllowUsers root' >> /etc/ssh/sshd_config
    #         echo 'AllowUsers recovery' >> /etc/ssh/sshd_config

    #         /etc/init.d/ssh restart
    #         """
    #     self.executeBashScript(CMDS)

    #     if sshkeypath != "":
    #         # play with paramiko to see if we can connect (ssh-agent will be used)
    #         ssh.connect(hostname, port=port, username="root", password=None, pkey=None,
    #                     key_filename=None, timeout=None, allow_agent=True, look_for_keys=False)
    #         ssh.close()
    #         print("ssh test with key ok")

    #     print("secure machine done")
