from Jumpscale import j

from .SSHKey import SSHKey


class SSHKeys(j.application.JSBaseConfigsClass):

    __jslocation__ = "j.clients.sshkey"
    _CHILDCLASS = SSHKey

    def _init(self):
        # self._sshagent = None
        self.SSHKey = SSHKey  # is the child class, can have more than 1

    def knownhosts_remove(self, item):
        """
        :param item: is ip addr or hostname to be removed from known_hosts
        :type item: str
        """
        path = "{DIR_HOME}/.ssh/known_hosts"
        if j.sal.fs.exists(path):
            out = ""
            for line in j.sal.fs.readFile(path).split("\n"):
                if line.find(item) is not -1:
                    continue
                out += "%s\n" % line
            j.sal.fs.writeFile(path, out)

    def test(self):
        '''
        -Generates key manually first
        -j.clients.sshkey.get(name="test",path="~/.ssh/test_key")
        -checks self.pubkey, self.privkey
        -deletes from ssh dir --> check path doesnt exist
        -writes to ssh dir --> check path exists
        -generate(reset=True)
        -checks saved sshkeys with sshkeys before generate and compare it after generate

        Agent:
        -checks is_loaded is False
        -loads keys to agent         -->check is_loaded is True
        -unloads sshkeys from agent  --> check is_loaded is False
        '''
        path = "/root/.ssh/test_key"
        sshkey_client = j.clients.sshkey.get(name="test_key", path=path)
        assert sshkey_client.path == path
        assert sshkey_client.privkey == j.sal.fs.readFile(path)
        assert sshkey_client.pubkey == j.sal.fs.readFile('%s.pub' % (path))

        try:
            sshkey_client.delete_from_sshdir()
        except ValueError as e:
            pass

        sshkey_client.write_to_sshdir()
        assert sshkey_client.privkey == j.sal.fs.readFile(path)
        assert sshkey_client.pubkey == j.sal.fs.readFile('%s.pub' % (path))

        old_pubkey = sshkey_client.pubkey
        old_privkey = sshkey_client.privkey
        sshkey_client.generate(reset=True)
        assert sshkey_client.privkey == j.sal.fs.readFile(path)
        assert sshkey_client.pubkey == j.sal.fs.readFile('%s.pub' % (path))
        assert sshkey_client.privkey != old_privkey
        assert sshkey_client.pubkey != old_pubkey
        sshkey_client.save()

        assert sshkey_client.is_loaded() == False
        sshkey_client.load()
        assert sshkey_client.is_loaded()
        sshkey_client.unload()
        assert sshkey_client.is_loaded() == False

        # Clean up after test
        sshkey_client.delete_from_sshdir()
        sshkey_client.delete()

