from Jumpscale import j
from .karkenClient import KrakenClient
JSConfigs = j.application.JSBaseConfigsClass


class KrakenFactory(JSConfigs):
    __jslocation__ = 'j.clients.kraken'
    _CHILDCLASS = KrakenClient

    def install(self, reset=False):
        j.builder.runtimes.pip.install("pykrakenapi", reset=reset)
        j.builder.runtimes.pip.install("krakenex", reset=reset)
