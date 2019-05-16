from Jumpscale import j
import subprocess


OP_ADD = "+"
OP_DEL = "-"
OP_ERS = "--"


class SSHD:

    __jslocation__ = "j.sal.sshd"

    def __init__(self):
        self._keys = None
        self._transactions = []

    @property
    def ssh_root_path(self):
        return j.tools.path.get(j.dirs.HOMEDIR).joinpath(".ssh")

    @property
    def ssh_authorized_keys_path(self):
        return j.tools.path.get(self.ssh_root_path).joinpath("authorized_keys")

    @property
    def keys(self):
        if self._keys is None:
            self.ssh_root_path.makedirs_p()
            if self.ssh_authorized_keys_path.exists():
                self._keys = self.ssh_authorized_keys_path.text().splitlines()
                self._keys = list(filter(None, self._keys))
            else:
                self._keys = []

        return self._keys

    def executer(self, cmd):
        cmd = cmd.split(" ")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def key_add(self, key):
        """ Add pubkey to authorized_keys
        :param key: public key which  will be added to authorized keys.
        :type key: string.
        """
        self._transactions.append((OP_ADD, key.strip()))

    def key_delete(self, key):
        """ Delete pubkey from authorized_keys
        :param key: public key which  will be deleted from authorized keys.
        :type key: string.
        """
        self._transactions.append((OP_DEL, key.strip()))

    def erase(self):
        """ Erase all keys from authorized_keys
        """
        self._transactions.append((OP_ERS, None))

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
            self.ssh_authorized_keys_path.write_text("\n".join(keys))
        self._keys = None

    def disable_none_key_access(self):
        """ Disable passowrd login to server
        This action doens't require calling to commit and applies immediately. 
        So if you added your key make sure to commit it before you call this method.

        'note': this is not a smart way to do this: there could be
        entries "PasswordAuthentication yes" already in the file
        """
        pth = j.tools.path.get("/etc/ssh/sshd_config")
        pth.write_text("PasswordAuthentication no", append=True)
        self.executer("service ssh restart")
