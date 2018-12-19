from Jumpscale import j
from .GrafanaClient import GrafanaClient

class GrafanaFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.clients._template"
    GrafanaClient = GrafanaClient

    def _init(self):
        self.clients={}


    def get(self,name,**kwargs):
        if name not in self.clients:
            cl = GrafanaClient(name=name)
            cl.data_update(**kwargs)
            self.clients[name] = cl
        return self.clients[name]


