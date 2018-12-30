from Jumpscale import j
import krakenex
from pykrakenapi import KrakenAPI

JSConfigClient = j.application.JSBaseConfigClass


class KrakenClient(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.kraken.clients
        name* = "" (S)
        api_key_ = "" (S)
        private_key_ = "" (S)
        """

    def _init(self):
        kraken_api = krakenex.API()
        kraken_api.key = self.api_key_
        kraken_api.secret = self.private_key_
        self.api = KrakenAPI(kraken_api)

    def test(self):

        k = self.api
        self._logger.debug("open orders")
        self._logger.debug(k.get_open_orders())

        self._logger.debug("get account balance")
        self._logger.debug(k.get_account_balance())
