"""
Client factory for the Tfchain network, js entry point
"""

from Jumpscale import j

from .TFChainClient import TFChainClient

from .TFChainExplorerClient import TFChainExplorerClient
from .types.Errors import ErrorTypes
from .TFChainTypesFactory import TFChainTypesFactory
from .TFChainTime import TFChainTime

JSConfigBaseFactory = j.application.JSFactoryConfigsBaseClass


class TFChainClientFactory(JSConfigBaseFactory):
    """
    Factory class to get a tfchain client object
    """

    __jslocation__ = "j.clients.tfchain"
    _CHILDCLASS = TFChainClient

    def _init(self, **kwargs):
        self._explorer_client = TFChainExplorerClient()
        self._types_factory = TFChainTypesFactory()
        self._error_types = ErrorTypes()
        self._time = TFChainTime()

    @property
    def time(self):
        return self._time

    @property
    def explorer(self):
        return self._explorer_client

    @property
    def types(self):
        return self._types_factory

    @property
    def errors(self):
        return self._error_types

    def test(self, name=""):
        """
        kosmos 'j.clients.tfchain.test()'
        :return:
        """
        self._test_run(name=name)
