from Jumpscale import j
from .GrafanaClient import GrafanaClient


class GrafanaFactory(j.application.JSBaseConfigsClass):

    __jslocation__ = "j.clients.grafana"
    _CHILDCLASS = GrafanaClient

    def _init(self, **kwargs):
        self.clients = {}
