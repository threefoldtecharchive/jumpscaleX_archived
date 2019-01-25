"""
Tfchain Client
"""

from Jumpscale import j


EXPLORER_NODES_STD = [
                'https://explorer.threefoldtoken.com',
                'https://explorer2.threefoldtoken.com',
                'https://explorer3.threefoldtoken.com',
                'https://explorer4.threefoldtoken.com',
            ]

EXPLORER_NODES_TEST = [
                'https://explorer.testnet.threefoldtoken.com',
                'https://explorer2.testnet.threefoldtoken.com',
            ]

EXPLORER_NODES_DEV = [
                'http://localhost:23112'
            ]


class TFChainClient(j.application.JSBaseConfigClass):
    """
    Tfchain client object
    """
    _SCHEMATEXT = """
        @url = jumpscale.tfchain.client
        name* = "" (S)
        network_type = "STD,TEST,DEV" (E)
        password = "" (S)
        minimum_minerfee = 100000000 (I)
        explorer_nodes = (LS)
        """

    def _data_trigger_new(self):
        if self.network_type == "STD":
            if len(self.explorer_nodes) == 0:
                self.explorer_nodes = EXPLORER_NODES_STD
        elif self.network_type == "TEST":
            if len(self.explorer_nodes) == 0:
                self.explorer_nodes = EXPLORER_NODES_TEST
        elif self.network_type == "DEV":
            self.minimum_minerfee = 1000000000
            if len(self.explorer_nodes) == 0:
                self.explorer_nodes = EXPLORER_NODES_DEV

    def transaction_get(self, txid):
        """
        Get a transaction from an available explorer Node.
        """
        txid = self._normalize_id(txid)
        resp = j.clients.tfchain.explorer.get(urls=self.explorer_nodes, endpoint="/explorer/hashes/"+txid)
        resp = data = j.data.serializers.json.loads(resp)
        assert resp['hashtype'] == 'transactionid'
        resp = resp['transaction']
        assert resp['id'] == txid
        return j.clients.tfchain.transactions.from_json(obj=resp['rawtransaction'], id=resp['id'])

    def _normalize_id(self, id):
        if isinstance(id, (bytes, bytearray)):
            id = id.hex()
        if type(id) is not str:
            raise TypeError("ID has to be a string")
        if len(id) != 64:
            raise TypeError("ID has to be hex-encoded and have a fixed length of 64")
        return id
