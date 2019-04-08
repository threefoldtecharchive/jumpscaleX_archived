from Jumpscale import j
from .SonicClient import SonicClient
JSConfigs = j.application.JSBaseConfigsClass

class SonicFactory(JSConfigs):

    """
    Sonic Client factory
    """

    __jslocation__ = "j.clients.sonic"
    _CHILDCLASS = SonicClient

    def _init(self):
        pass