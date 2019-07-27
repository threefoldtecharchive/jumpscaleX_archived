from Jumpscale import j
from .Syncer import Syncer


class SyncerFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = "j.tools.syncer"

    _CHILDCLASS = Syncer

    def sync(self, monitor=False):
        """
        execute to sync all syncers
        will push default code directories to remove ssh host
        """
        for name in self._children:
            self.syncers[name].sync()

        if monitor:
            self.monitor()

    def test(self):
        """
        kosmos 'j.tools.syncer.test()'
        :return:
        """

        cl = j.clients.ssh.get(name="docker", addr="localhost", port=9122)
        cl.save()

        cl2 = j.clients.ssh.get(name="docker2", addr="localhost", port=9122)
        cl2.save()

        s = j.tools.syncer.get()

        s.sshclients_add([cl, cl2])

        s.sync(monitor=True)

        # r = cl.execute("ls / ")

        j.shell()

        s = self.get(name="builder", sshclient_name=cl.name, paths=None)
        s.sync()
