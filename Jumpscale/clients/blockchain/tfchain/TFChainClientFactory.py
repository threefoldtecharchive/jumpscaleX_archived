"""
Client factory for the Tfchain network, js entry point
"""

from Jumpscale import j

from .TFChainExplorerClient import TFChainExplorerClient
from .TFChainClient import TFChainClient

class TfchainClientFactory(j.application.JSBaseConfigsClass):
    """
    Factory class to get a tfchain client object
    """
    __jslocation__ = "j.clients.tfchain"
    _CHILDCLASS = TFChainClient

    @property
    def explorer(self):
        return TFChainExplorerClient()
