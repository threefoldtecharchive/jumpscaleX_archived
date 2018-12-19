from Jumpscale import j
from .Syncer import Syncer

class SyncerFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.tools.syncer"

    Syncer=Syncer

    def _init(self):
        self.syncers = {}

    def get(self,name,**kwargs):
        if name not in self.syncers:
            s = Syncer(name=name)
            s.data_update(**kwargs)
            self.syncers[name] = s
        return self.syncers[name]

    def sync(self):
        """
        execute to sync all syncers


        """
        j.shell()

    def test(self):
        """
        js_shell 'j.tools.syncer.test()'
        :return:
        """
        s = self.get(name="default",addr="10.102.133.88",port="1053")
        s.sync()
