from Jumpscale import j
from .Syncer import Syncer


class SyncerFactory(j.application.JSFactoryBaseClass):
    __jslocation__ = "j.tools.syncer"

    _CHILDCLASS = Syncer

    def _init(self):
        self.syncers = {}

    def sync(self):
        """
        execute to sync all syncers
        will push default code directories to remove ssh host
        """
        for name in self.syncers:
            self.syncers[name].sync()

    def test(self):
        """
        js_shell 'j.tools.syncer.test()'
        :return:
        """
        s = self.get(name="default", addr="172.17.0.2", port=22)
        s.sync()
