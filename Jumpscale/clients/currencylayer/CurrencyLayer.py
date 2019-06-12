from pprint import pprint as print
import cryptocompare as cc
from Jumpscale import j


class CurrencyLayerFactory(j.application.JSBaseConfigClass):
    """
    get key from https://currencylayer.com/quickstart
    """

    __jslocation__ = "j.clients.currencylayer"

    _SCHEMATEXT = """
    @url = jumpscale.currencylayer.client
    name* = "" (S)
    api_key_ = "" (S)
    """

    def _init(self):
        self._data_cur = {}
        self._id2cur = {}
        self._cur2id = {}
        self.fallback = True
        self.fake = False
        self.api_key_ = "02fe99e9cefaf1733c299a19eaff1cf6"
        self._data_path = "%s/data.toml" % self._dirpath

    def _write_default(self):
        """
        will write default data for the currencies to local directory
        """
        if j.sal.fs.exists(self._data_path):
            s = j.sal.fs.statPath(self._data_path)
            if j.data.time.epoch - (3600 * 24 * 7) < int(s.st_mtime):
                return  # means do not have to write, because not old enough
        j.data.serializers.toml.dump(self._data_path, self._data_cur)

    def _load_default(self):
        return j.data.serializers.toml.load(self._data_path)

    def fetch(self, reset=False):
        """
        kosmos 'j.clients.currencylayer.fetch()'

        will get the most recent data from the internet

        """
        if reset:
            self._cache.reset()

        def get():
            if not self.fake and j.sal.nettools.tcpPortConnectionTest("currencylayer.com", 443):
                key = self.api_key_
                if key.strip():
                    url = "http://apilayer.net/api/live?access_key=%s" % key

                    c = j.clients.http.getConnection()
                    r = c.get(url).readlines()

                    data = r[0].decode()
                    data = j.data.serializers.json.loads(data)["quotes"]

                    data["USDETH"] = 1 / cc.get_price("ETH", "USD")["ETH"]["USD"]
                    data["USDXRP"] = cc.get_price("USD", "XRP")["USD"]["XRP"]
                    data["USDBTC"] = 1 / cc.get_price("BTC", "USD")["BTC"]["USD"]

                    self._log_error("fetch currency from internet")
                    return data
                elif not self.fallback:
                    raise RuntimeError("api key for currency layer " "needs to be specified")
                else:
                    self._log_warning("currencylayer api_key not set, " "use fake local data.")
                    return self._load_default()

            if self.fake or self.fallback:
                self._log_warning("cannot reach: currencylayer.com, " "use fake local data.")
                return self._load_default()
            raise RuntimeError("could not data from currencylayers")

        data = self._cache.get("currency_data", get, expire=3600 * 24)
        for key, item in data.items():
            if key.startswith("USD"):
                key = key[3:]
                self._data_cur[key.lower()] = item
        self._write_default()

    @property
    def cur2usd(self):
        """
        e.g. AED = 3,672 means 3,6... times AED=1 USD

        kosmos 'j.clients.currencylayer.cur2usd_print()'
        """
        if self._data_cur == {}:
            self.fetch()
        return self._data_cur

    def cur2usd_print(self):
        print(self.cur2usd)

    @property
    def id2cur(self):
        """
        """
        if self._id2cur == {}:
            from .currencies_id import currencies_id

            self._id2cur = currencies_id
        return self._id2cur

    @property
    def cur2id(self):
        """
        """
        if self._cur2id == {}:
            res = {}
            for key, val in self.id2cur.items():
                res[val] = key
            self._cur2id = res
        return self._cur2id

    def id2cur_print(self):
        """
        kosmos 'j.clients.currencylayer.id2cur_print()'
        """
        print(self.id2cur)

    def cur2id_print(self):
        """
        kosmos 'j.clients.currencylayer.cur2id_print()'
        """
        print(self.cur2id)

    def test(self):
        """
        kosmos 'j.clients.currencylayer.test()'
        """
        self.fetch()
        self.id2cur_print()
        self._log_info(self.cur2usd)
        assert "aed" in self.cur2usd
