from Jumpscale import j
from .PortalClient import PortalClient

JSConfigFactory = j.application.JSFactoryBaseClass


class PortalClientFactory(JSConfigFactory):
    __jslocation__ = "j.clients.portal"
    _CHILDCLASS = PortalClient

    def _init(self):
        self._portalClients = {}
