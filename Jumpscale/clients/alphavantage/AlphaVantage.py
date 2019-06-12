from pprint import pprint as print
import cryptocompare as cc
from Jumpscale import j


class AlphaVantageClient(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    @url = jumpscale.alphavantage.client
    name* = "" (S)
    api_key_ = "" (S)
    """

    def _init(self):
        self._client = None

    @property
    def client(self):
        if not self._client:
            try:
                from alpha_vantage.timeseries import TimeSeries
            except Exception as e:
                j.shell()
            self._client = TimeSeries(key=self.api_key_, output_format="csv ")
        return self._client


class AlphaVantageFactory(j.application.JSBaseConfigsClass):
    """
    get key https://www.alphavantage.co
    """

    __jslocation__ = "j.clients.alphavantage"

    _CHILDCLASS = AlphaVantageSingleton

    def _init(self):
        pass

    def install(self):
        j.shell()

    def test(self):
        """
        kosmos 'j.clients.alphavantage.test()'
        """
        # self.new("main", api_key_="....")
        cl = self.main.client
        j.shell()