from Jumpscale import j
from .Syncer import Syncer


class SyncerFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = "j.tools.syncer"

    _CHILDCLASS = Syncer

    def sync(self):
        """
        execute to sync all syncers
        will push default code directories to remove ssh host
        """
        for name in self._children:
            self.syncers[name].sync()

    def test(self):
        """
        js_shell 'j.tools.syncer.test()'
        :return:
        """
        cl = j.clients.ssh.get(name="builder", addr="10.102.133.88", port=1053)
        r = cl.execute("ls / ")

        s = self.get(name="builder", sshclient_name=cl.name, paths=None)
        s.sync()
