from Jumpscale import j

import re

from Jumpscale.clients.blockchain.tfchain.types.Errors import ExplorerNoContent

class TFChainExplorerGetClientStub(j.application.JSBaseClass):
    def __init__(self):
        self._blocks = {}
        self._hashes = {}
        self._chain_info = None
        self._expected_transactions = []

    @property
    def chain_info(self):
        if not self._chain_info:
            raise Exception("chain info not set in stub client")
        return self._chain_info
    @chain_info.setter
    def chain_info(self, value):
        assert isinstance(value, str) and len(value) > 2
        self._chain_info = value

    def add_expected_transaction(self, transactionid, resp):
        """
        To facilitate transaction positing in an emulated way.
        """
        assert isinstance(transactionid, str)
        assert isinstance(resp, str)
        self._expected_transactions.append((transactionid, resp))
    
    def explorer_get(self, endpoint):
        """
        Get explorer data from the stub client for the specified endpoint.
        """
        hash_template = re.compile(r'^.*/explorer/hashes/(.+)$')
        match = hash_template.match(endpoint)
        if match:
            return self.hash_get(match.group(1))
        hash_template = re.compile(r'^.*/explorer/blocks/(\d+)$')
        match = hash_template.match(endpoint)
        if match:
            return self.block_get(int(match.group(1)))
        info_template = re.compile(r'^.*/explorer$')
        if info_template.match(endpoint):
            return self.chain_info
        raise Exception("invalid endpoint {}".format(endpoint))

    def explorer_post(self, endpoint, data):
        """
        Put explorer data onto the stub client for the specified endpoint.
        """
        if not isinstance(data, dict):
            raise TypeError("data was expected to be of type dict not of type {}".format(type(data)))
        hash_template = re.compile(r'^.*/transactionpool/transactions$')
        match = hash_template.match(endpoint)
        if match:
            (txid, resp) = self._expected_transactions.pop()
            resp = j.data.serializers.json.loads(resp)
            resp['transaction']['rawtransaction'] = data
            resp = j.data.serializers.json.dumps(resp)
            pattern = re.compile(r'\s+')
            resp = re.sub(pattern, '', resp)
            self.hash_add(txid, resp)
            return '{"transactionid":"%s"}'%(txid)
        raise Exception("invalid endpoint {}".format(endpoint))

    def block_get(self, height):
        """
        The explorer block response at the given height.
        """
        assert isinstance(height, int)
        if not height in self._blocks:
            raise ExplorerNoContent("no content found for block {}".format(height), endpoint="/explorer/blocks/{}".format(height))
        return self._blocks[height]

    def block_add(self, height, resp):
        """
        Add a block response to the stub explorer at the given height.
        """
        assert isinstance(height, int)
        assert isinstance(resp, str)
        if height in self._blocks:
            raise KeyError("{} already exists in explorer blocks".format(height))
        self._blocks[height] = resp

    def hash_get(self, hash):
        """
        The explorer hash response at the given hash.
        """
        assert isinstance(hash, str)
        if not hash in self._hashes:
            raise ExplorerNoContent("no content found for hash {}".format(hash), endpoint="/explorer/hashes/{}".format(str(hash)))
        return self._hashes[hash]
    
    def hash_add(self, hash, resp):
        """
        Add a hash response to the stub explorer at the given hash.
        """
        assert isinstance(hash, str)
        assert isinstance(resp, str)
        if hash in self._hashes:
            raise KeyError("{} already exists in explorer hashes".format(hash))
        self._hashes[hash] = resp
