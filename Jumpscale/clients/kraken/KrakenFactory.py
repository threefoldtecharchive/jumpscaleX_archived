from Jumpscale import j
from .karkenClient import KrakenClient
JSConfigFactory = j.application.JSFactoryBaseClass


class KrakenFactory(JSConfigFactory):
    __jslocation__ = 'j.clients.kraken'
    _CHILDCLASS = KrakenClient

    def install(self, reset=False):
        j.builder.runtimes.pip.install("pykrakenapi", reset=reset)
        j.builder.runtimes.pip.install("krakenex", reset=reset)
