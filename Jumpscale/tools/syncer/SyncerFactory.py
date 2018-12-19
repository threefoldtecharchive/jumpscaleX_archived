from Jumpscale import j
from .Syncer import Syncer

class SyncerFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.tools.syncer"

    _CHILDCLASS = Syncer

    def _init(self):
        self.syncers = {}

    #SHOULD BE AUTOMATIC
    # def get(self,name,**kwargs):
    #     if name not in self.syncers:
    #         s = Syncer(name=name)
    #         s.data_update(**kwargs)
    #         self.syncers[name] = s
    #     return self.syncers[name]

    def sync(self):
        """
        execute to sync all syncers

        will push default code directories to remove ssh host

        """
        j.shell()

    def test(self):
        """
        js_shell 'j.tools.syncer.test()'
        :return:
        """
        s = self.get(name="default",addr="10.102.133.88",port="1053")
        s.sync()
