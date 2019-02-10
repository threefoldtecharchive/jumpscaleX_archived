from Jumpscale import j

import re

from Jumpscale.clients.blockchain.tfchain.types.Errors import ExplorerNoContent
from Jumpscale.clients.blockchain.tfchain.types.PrimitiveTypes import Hash

class TFChainExplorerGetClientStub(j.application.JSBaseClass):
    def __init__(self):
        self._blocks = {}
        self._hashes = {}
        self._chain_info = None
        self._posted_transactions = {}

    @property
    def chain_info(self):
        if not self._chain_info:
            raise Exception("chain info not set in stub client")
        return self._chain_info
    @chain_info.setter
    def chain_info(self, value):
        assert isinstance(value, str) and len(value) > 2
        self._chain_info = value

    def posted_transaction_get(self, transactionid):
        """
        Get a posted transaction using our random generated transaction ID.
        """
        if isinstance(transactionid, Hash):
            transactionid = str(transactionid)
        else:
            assert isinstance(transactionid, str)
        return self._posted_transactions[transactionid]
    
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
        hash_template = re.compile(r'^.*/transactionpool/transactions$')
        match = hash_template.match(endpoint)
        if match:
            transactionid = str(Hash(value=j.data.idgenerator.generateXByteID(Hash.SIZE)))
            transaction = j.clients.tfchain.transactions.from_json(data)
            # ensure all coin outputs and block stake outputs have identifiers set
            for idx, co in enumerate(transaction.coin_outputs):
                co.id = transaction.coin_outputid_new(idx)
            for idx, bso in enumerate(transaction.blockstake_outputs):
                bso.id = transaction.blockstake_outputid_new(idx)
            self._posted_transactions[transactionid] = transaction
            return '{"transactionid":"%s"}'%(str(transactionid))
        raise Exception("invalid endpoint {}".format(endpoint))

    def block_get(self, height):
        """
        The explorer block response at the given height.
        """
        assert isinstance(height, int)
        if not height in self._blocks:
            raise ExplorerNoContent("no content found for block {}".format(height), endpoint="/explorer/blocks/{}".format(height))
        return self._blocks[height]

    def block_add(self, height, resp, force=False):
        """
        Add a block response to the stub explorer at the given height.
        """
        assert isinstance(height, int)
        assert isinstance(resp, str)
        if not force and height in self._blocks:
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
    
    def hash_add(self, hash, resp, force=False):
        """
        Add a hash response to the stub explorer at the given hash.
        """
        assert isinstance(hash, str)
        assert isinstance(resp, str)
        if not force and hash in self._hashes:
            raise KeyError("{} already exists in explorer hashes".format(hash))
        self._hashes[hash] = resp
