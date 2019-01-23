from Jumpscale import j

from .SSHKey import SSHKey


class SSHKeys(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.clients.sshkey"
    _CHILDCLASS = SSHKey

    def _init(self):
        # self._sshagent = None
        self.SSHKey = SSHKey  # is the child class, can have more than 1

    def knownhosts_remove(self, item):
        '''Remove known hosts

        :param item: is ip addr or hostname to be removed from known_hosts
        :type item: str
        '''
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
