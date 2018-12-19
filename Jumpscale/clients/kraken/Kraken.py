from Jumpscale import j


TEMPLATE = """
api_key_ = ""
private_key_ = ""
"""

JSConfigClient = j.application.JSBaseClass
JSConfigFactory = j.application.JSFactoryBaseClass


class KrakenClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        import krakenex
        from pykrakenapi import KrakenAPI

        kraken_api = krakenex.API()
        kraken_api.key = self.config.data["api_key_"]
        kraken_api.secret = self.config.data["private_key_"]
        self.api = KrakenAPI(kraken_api)

    def test(self):

        k = self.api
        self._logger.debug("open orders")
        self._logger.debug(k.get_open_orders())

        self._logger.debug("get account balance")
        self._logger.debug(k.get_account_balance())

class Kraken(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = 'j.clients.kraken'
        JSConfigFactory.__init__(self, KrakenClient)

    def install(self, reset=False):
        j.tools.prefab.local.runtimes.pip.install("pykrakenapi", reset=reset)
        j.tools.prefab.local.runtimes.pip.install("krakenex", reset=reset)
