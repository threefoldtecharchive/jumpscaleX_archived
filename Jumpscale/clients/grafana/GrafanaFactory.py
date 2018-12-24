from Jumpscale import j
from .GrafanaClient import GrafanaClient


class GrafanaFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.clients.grafana"
    _CHILDCLASS = GrafanaClient

    def _init(self):
        self.clients = {}
