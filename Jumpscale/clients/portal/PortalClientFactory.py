from Jumpscale import j
from .PortalClient import PortalClient

JSConfigs = j.application.JSBaseConfigsClass


class PortalClientFactory(JSConfigs):
    __jslocation__ = "j.clients.portal"
    _CHILDCLASS = PortalClient

    def _init(self, **kwargs):
        self._portalClients = {}
