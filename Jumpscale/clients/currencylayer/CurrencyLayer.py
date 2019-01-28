from pprint import pprint as print
import cryptocompare as cc
from Jumpscale import j


class CurrencyLayerSingleton(j.application.JSBaseConfigClass):
    """
    get key from https://currencylayer.com/quickstart
    """

    __jslocation__ = 'j.clients.currencylayer'


    _SCHEMATEXT = """
    @url = jumpscale.currencylayer.client
    name* = "" (S)
    api_key_ = "" (S)
    """


    def __init__(self):
        factory = CurrencyLayerFactory() #get access to factory, then give to only child = singleton
        j.application.JSBaseConfigClass.__init__(self,name="main",factory=factory)

    def _init(self):
        self._data_cur = {}
        self._id2cur = {}
        self._cur2id = {}
        self.fallback = True
        self.fake = True  # otherone is broken for now, will have to fix

    def write_default(self):
        """ will load currencies from internet and then write to currencies.py 
            in the extension directory
        """
        raise NotImplementedError()
        # TODO:*2

    def load(self, reset=False):
        """ js_shell 'j.clients.currencylayer.load()'
        """
        if reset:
            self._cache.reset()

        def get():
            if not self.fake and \
                    j.sal.nettools.tcpPortConnectionTest("currencylayer.com", 443):
                key = self.api_key_
                if key.strip():
                    url = "http://apilayer.net/api/live?access_key=%s" % key

                    c = j.clients.http.getConnection()
                    r = c.get(url).readlines()

                    data = r[0].decode()
                    data = j.data.serializers.json.loads(data)["quotes"]

                    data['USDETH'] = 1/cc.get_price('ETH', 'USD')['ETH']['USD']
                    data['USDXRP'] = cc.get_price('USD', 'XRP')['USD']['XRP']
                    data['USDBTC'] = 1/cc.get_price('BTC', 'USD')['BTC']['USD']

                    self._logger.error("fetch currency from internet")
                    return data
                elif not self.fallback:
                    raise RuntimeError("api key for currency layer "
                                       "needs to be specified")
                else:
                    self._logger.warning("currencylayer api_key not set, "
                                         "use fake local data.")

            if self.fake or self.fallback:
                self._logger.warning("cannot reach: currencylayer.com, "
                                     "use fake local data.")
                from .currencies import currencies
                return currencies
            raise RuntimeError("could not data from currencylayers")

        data = self._cache.get("currency_data", get, expire=3600 * 24)
        for key, item in data.items():
            if key.startswith("USD"):
                key = key[3:]
            self._data_cur[key.lower()] = item

    @property
    def cur2usd(self):
        """
        e.g. AED = 3,672 means 3,6... times AED=1 USD

        js_shell 'j.clients.currencylayer.cur2usd_print()'
        """
        if self._data_cur == {}:
            self.load()
        return self._data_cur

    def cur2usd_print(self):
        print(self.cur2usd)

    @property
    def id2cur(self):
        """
        """
        # def produce(): #ONLY DO THIS ONCE EVER !!!
        #     keys = [item for item in self.cur2usd.keys()]
        #     keys.sort()
        #     nr=0
        #     res={}
        #     for key in keys:
        #         nr+=1
        #         res[nr] = key
        #     return res
        if self._id2cur == {}:
            from .currencies_id import currencies_id
            self._id2cur = currencies_id
        return self._id2cur

    @property
    def cur2id(self):
        """
        """
        # def produce(): #ONLY DO THIS ONCE EVER !!!
        #     keys = [item for item in self.cur2usd.keys()]
        #     keys.sort()
        #     nr=0
        #     res={}
        #     for key in keys:
        #         nr+=1
        #         res[nr] = key
        #     return res
        if self._cur2id == {}:
            res = {}
            for key, val in self.id2cur.items():
                res[val] = key
            self._cur2id = res
        return self._cur2id

    def id2cur_print(self):
        """
        js_shell 'j.clients.currencylayer.id2cur_print()'
        """
        pprint(self.id2cur)

    def cur2id_print(self):
        """
        js_shell 'j.clients.currencylayer.cur2id_print()'
        """
        pprint(self.cur2id)

    def test(self):
        """
        js_shell 'j.clients.currencylayer.test()'
        """
        r=j.clients.currencylayer._Find()
        j.shell()
        self._logger.info(self.cur2usd)
        assert 'aed' in self.cur2usd

class CurrencyLayerFactory(j.application.JSBaseConfigsClass):

    _CHILDCLASS = CurrencyLayerSingleton

