"""
Tfchain Client
"""

from Jumpscale import j

from TFChainClient import TFChainClient

class TFChainClients(j.application.JSBaseConfigsClass):
    """
    factory for the clients
    """

    _CHILDCLASS = TFChainClient

    def _childclass_selector(self):

        return TFChainClient

