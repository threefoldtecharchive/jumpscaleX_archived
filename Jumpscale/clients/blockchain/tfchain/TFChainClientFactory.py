"""
Client factory for the Tfchain network, js entry point
"""

from Jumpscale import j

from .TFChainClient import TFChainClient

from .TFChainExplorerClient import TFChainExplorerClient
from .TFChainTransactionFactory import TFChainTransactionFactory
from .TFChainTypesFactory import TFChainTypesFactory


class TFChainClientFactory(j.application.JSBaseConfigsClass):
    """
    Factory class to get a tfchain client object
    """
    __jslocation__ = "j.clients.tfchain"
    _CHILDCLASS = TFChainClient

    @property
    def explorer(self):
        return TFChainExplorerClient()

    @property
    def transactions(self):
        return TFChainTransactionFactory()

    @property
    def types(self):
        return TFChainTypesFactory()
