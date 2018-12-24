from Jumpscale import j

from .SSHKey import SSHKey


class SSHKeys(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.clients.sshkey"
    _CHILDCLASS = SSHKey

    def _init(self):
        # self._sshagent = None
        self.SSHKey = SSHKey  # is the child class, can have more than 1

    def get(self, name=None, **kwargs):
        """

        :param name: name of the connection and the ssh key as loaded in sshagent
           if name is none then will see if there is 1 key loaded in sshagent and then use that one
        :return:
        """
        if name is None:
            name = j.clients.sshagent.keyname_default
        sshkey = self.SSHKey(name=name)
        sshkey.data_update(**kwargs)
        return sshkey

    def knownhosts_remove(self, item):
        """
        :param item: is ip addr or hostname to be removed from known_hosts
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
        """
        js_shell 'j.clients.sshkey.test()'
        """

        self._logger_enable()
        j.shell()
        # TODO:
