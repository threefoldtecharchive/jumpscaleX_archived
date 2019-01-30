from Jumpscale import j

import re

from Jumpscale.clients.blockchain.tfchain.types.errors import ExplorerNoContent

class TFChainExplorerGetClientStub(j.application.JSBaseClass):
    def __init__(self):
        self._blocks = {}
        self._hashes = {}
        self._chain_info = None

    @property
    def chain_info(self):
        if not self._chain_info:
            raise Exception("chain info not set in stub client")
        return self._chain_info
    @chain_info.setter
    def chain_info(self, value):
        assert isinstance(value, str) and len(value) > 2
        self._chain_info = value
    
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

    def block_get(self, height):
        """
        The explorer block response at the given height.
        """
        assert isinstance(height, int)
        if not height in self._blocks:
            raise ExplorerNoContent("no content found for block {}".format(height))
        return self._blocks[height]

    def block_add(self, height, resp):
        """
        Add a block response to the stub explorer at the given height.
        """
        assert isinstance(height, int)
        assert isinstance(resp, str)
        self._blocks[height] = resp

    def hash_get(self, hash):
        """
        The explorer hash response at the given hash.
        """
        assert isinstance(hash, str)
        if not hash in self._hashes:
            raise ExplorerNoContent("no content found for hash {}".format(hash))
        return self._hashes[hash]
    
    def hash_add(self, hash, resp):
        """
        Add a hash response to the stub explorer at the given hash.
        """
        assert isinstance(hash, str)
        assert isinstance(resp, str)
        self._hashes[hash] = resp
