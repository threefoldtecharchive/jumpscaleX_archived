from Jumpscale import j
from .GrafanaClient import GrafanaClient

class GrafanaFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.clients._template"
    _CHILDCLASS = GrafanaClient

    def _init(self):
        self.clients={}

    def test(self):
        self.get(url="...",name="sss")
        self.count()
        self.find()  #TODO: will find all
        self.find(url="ss")  #TODO: check
