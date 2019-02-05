"""
Tfchain Client
"""

from Jumpscale import j
from .types.ConditionTypes import UnlockHash, UnlockHashType
from .types.PrimitiveTypes import Hash, Currency
from .types.CompositionTypes import CoinOutput
from .types.Errors import ExplorerInvalidResponse
from .TFChainTransactionFactory import TransactionBaseClass
from .TFChainWalletFactory import TFChainWalletFactory

_EXPLORER_NODES = {
    "STD": [
        'https://explorer.threefoldtoken.com',
        'https://explorer2.threefoldtoken.com',
        'https://explorer3.threefoldtoken.com',
        'https://explorer4.threefoldtoken.com',
    ],
    "TEST": [
        'https://explorer.testnet.threefoldtoken.com',
        'https://explorer2.testnet.threefoldtoken.com',
    ],
    "DEV": [
        'http://localhost:23110'
    ],
}

_CHAIN_NETWORK_TYPES = sorted(['STD', 'TEST', 'DEV'])

class TFChainClient(j.application.JSBaseConfigParentClass):
    """
    Tfchain client object
    """
    _SCHEMATEXT = """
        @url = jumpscale.tfchain.client
        name* = "" (S)
        network_type = "STD,TEST,DEV" (E)
        explorer_nodes = (LS) !jumpscale.tfchain.explorer
        """

    _CHILDCLASSES = [TFChainWalletFactory]

    @property
    def explorer_addresses(self):
        """
        Addresses of the explorers to use
        """
        if len(self.explorer_nodes) > 0:
            return self.explorer_nodes.pylist()
        return _EXPLORER_NODES[self.network]

    @property
    def network(self):
        # TODO: REMOVE THIS HACK,
        #       used to work fine as-is, but it seems JSX now also can return Enum values
        #       as raw integers, which breaks my default logic here,
        #       only occurs when loaded from a saved instance,
        #       so there must be something going wrong during decoding.
        if isinstance(self.network_type, int):
            self.network_type = _CHAIN_NETWORK_TYPES[self.network_type-1]
        return self.network_type

    @property
    def minimum_minerfee(self):
        if self.network == "DEV":
            return 1000000000
        return 100000000

    def blockchain_info_get(self):
        """
        Get the current blockchain info, using the last known block, as reported by an explorer.
        """
        resp = self._explorer_get(endpoint="/explorer")
        resp = j.data.serializers.json.loads(resp)
        blockid = Hash.from_json(obj=resp['blockid'])
        last_block = self.block_get(blockid)
        return ExplorerBlockchainInfo(last_block=last_block)

    def block_get(self, value):
        """
        Get a block from an available explorer Node.
        
        @param value: the identifier or height that points to the desired block
        """
        endpoint = "/explorer/?"
        resp = {}
        try:
            # get the explorer block
            if isinstance(value, int):
                endpoint = "/explorer/blocks/{}".format(int(value))
                resp = self._explorer_get(endpoint=endpoint)
                resp = j.data.serializers.json.loads(resp)
                resp = resp['block']
            else:
                blockid = self._normalize_id(value)
                endpoint = "/explorer/hashes/"+blockid
                resp = self._explorer_get(endpoint=endpoint)
                resp = j.data.serializers.json.loads(resp)
                if resp['hashtype'] != 'blockid':
                    raise ExplorerInvalidResponse("expected hash type 'blockid' not '{}'".format(resp['hashtype']), endpoint, resp)
                resp = resp['block']
                if resp['blockid'] != blockid:
                    raise ExplorerInvalidResponse("expected block ID '{}' not '{}'".format(blockid, resp['blockid']), endpoint, resp)
            # parse the transactions
            transactions = []
            for etxn in resp['transactions']:
                # parse the explorer transaction
                transaction = self._transaction_from_explorer_transaction(etxn, endpoint=endpoint, resp=resp)
                # append the transaction to the list of transactions
                transactions.append(transaction)
            rawblock = resp['rawblock']
            # parse the parent id
            parentid = Hash.from_json(obj=rawblock['parentid'])
            # parse the miner payouts
            miner_payouts = []
            minerpayoutids = resp.get('minerpayoutids', None) or []
            eminerpayouts = rawblock.get('minerpayouts', None) or []
            if len(eminerpayouts) != len(minerpayoutids):
                raise ExplorerInvalidResponse("amount of miner payouts and payout ids are not matching: {} != {}".format(len(eminerpayouts), len(minerpayoutids)), endpoint, resp)
            for idx, mp in enumerate(eminerpayouts):
                id = Hash.from_json(minerpayoutids[idx])
                value = Currency.from_json(mp['value'])
                unlockhash = UnlockHash.from_json(mp['unlockhash'])
                miner_payouts.append(ExplorerMinerPayout(id=id, value=value, unlockhash=unlockhash))
            # get the timestamp and height
            height = int(resp['height'])
            timestamp = int(rawblock['timestamp'])
            # get the block's identifier
            blockid = Hash.from_json(resp['blockid'])
            # return the block, as reported by the explorer
            return ExplorerBlock(
                id=blockid, parentid=parentid,
                height=height, timestamp=timestamp,
                transactions=transactions, miner_payouts=miner_payouts)
        except KeyError as msg:
            # return a KeyError as an invalid Explorer Response
            raise ExplorerInvalidResponse(msg, endpoint, resp)

    def transaction_get(self, txid):
        """
        Get a transaction from an available explorer Node.
        
        @param txid: the identifier (fixed string with a length of 64) that points to the desired transaction
        """
        txid = self._normalize_id(txid)
        endpoint = "/explorer/hashes/"+txid
        resp = self._explorer_get(endpoint=endpoint)
        resp = j.data.serializers.json.loads(resp)
        try:
            if resp['hashtype'] != 'transactionid':
                raise ExplorerInvalidResponse("expected hash type 'transactionid' not '{}'".format(resp['hashtype']), endpoint, resp)
            resp = resp['transaction']
            if resp['id'] != txid:
                raise ExplorerInvalidResponse("expected transaction ID '{}' not '{}'".format(txid, resp['id']), endpoint, resp)
            return self._transaction_from_explorer_transaction(resp, endpoint=endpoint, resp=resp)
        except KeyError as msg:
            # return a KeyError as an invalid Explorer Response
            raise ExplorerInvalidResponse(msg, endpoint, resp)

    def transaction_put(self, transaction):
        """
        Submit a transaction to an available explorer Node.

        @param transaction: the transaction to push to the client transaction pool
        """
        if isinstance(transaction, TransactionBaseClass):
            transaction = transaction.json()
        endpoint = "/transactionpool/transactions"
        resp = self._explorer_post(endpoint=endpoint, data=transaction)
        resp = j.data.serializers.json.loads(resp)
        try:
            return str(Hash(value=resp['transactionid']))
        except KeyError as msg:
            # return a KeyError as an invalid Explorer Response
            raise ExplorerInvalidResponse(msg, endpoint, resp)
    
    def unlockhash_get(self, unlockhash):
        """
        Get all transactions linked to the given unlockhash,
        as well as other information such as the multisig addresses linked to the given unlockhash.

        @param unlockhash: the unlockhash to look up transactions for in the explorer
        """
        unlockhash = self._normalize_unlockhash(unlockhash)
        endpoint = "/explorer/hashes/"+unlockhash
        resp = self._explorer_get(endpoint=endpoint)
        resp = j.data.serializers.json.loads(resp)
        try:
            if resp['hashtype'] != 'unlockhash':
                raise ExplorerInvalidResponse("expected hash type 'unlockhash' not '{}'".format(resp['hashtype']), endpoint, resp)
            # parse the transactions
            transactions = []
            for etxn in resp['transactions']:
                # parse the explorer transaction
                transaction = self._transaction_from_explorer_transaction(etxn, endpoint=endpoint, resp=resp)
                # append the transaction to the list of transactions
                transactions.append(transaction)
            # collect all multisig addresses
            multisig_addresses = [UnlockHash.from_json(obj=uh) for uh in resp.get('multisigaddresses', None) or []]
            for addr in multisig_addresses:
                if addr.type != UnlockHashType.MULTI_SIG:
                    raise ExplorerInvalidResponse("invalid unlock hash type {} for MultiSignature Address (expected: 3)".format(addr.type), endpoint, resp)
            # TODO: support resp.get('erc20info')
            # return explorer data for the unlockhash
            return ExplorerUnlockhashResult(
                unlockhash=UnlockHash.from_json(unlockhash),
                transactions=transactions,
                multisig_addresses=multisig_addresses)
        except KeyError as msg:
            # return a KeyError as an invalid Explorer Response
            raise ExplorerInvalidResponse(msg, endpoint, resp)
    
    def mint_condition_get(self, height=None):
        """
        Get the latest (coin) mint condition or the (coin) mint condition at the specified block height.

        @param height: if defined the block height at which to look up the (coin) mint condition (if none latest block will be used)
        """
        # define the endpoint
        endpoint = "/explorer/mintcondition"
        if height is not None:
            if not isinstance(height, (int, str)):
                raise TypeError("invalid block height given")
            height = int(height)
            endpoint += "/%d"%(height)

        # get the mint condition
        resp = self._explorer_get(endpoint=endpoint)
        resp = j.data.serializers.json.loads(resp)

        try:
            # return the decoded mint condition
            return j.clients.tfchain.types.conditions.from_json(obj=resp['mintcondition'])
        except KeyError as msg:
            # return a KeyError as an invalid Explorer Response
            raise ExplorerInvalidResponse(msg, endpoint, resp)

    def _transaction_from_explorer_transaction(self, etxn, endpoint="/?", resp=None): # keyword parameters for error handling purposes only
        if resp is None:
            resp = {}
        # parse the transactions
        transaction = j.clients.tfchain.transactions.from_json(obj=etxn['rawtransaction'], id=etxn['id'])
        # add the parent (coin) outputs
        coininputoutputs = etxn.get('coininputoutputs', None) or []
        if len(transaction.coin_inputs) != len(coininputoutputs):
            raise ExplorerInvalidResponse("amount of coin inputs and parent outputs are not matching: {} != {}".format(len(transaction.coin_inputs), len(coininputoutputs)), endpoint, resp)
        for (idx, co) in enumerate(coininputoutputs):
            co = CoinOutput.from_json(obj=co)
            co.id = transaction.coin_inputs[idx].parentid
            transaction.coin_inputs[idx].parent_output = co
        # add the coin output ids
        coinoutputids = etxn.get('coinoutputids', None) or []
        if len(transaction.coin_outputs) != len(coinoutputids):
            raise ExplorerInvalidResponse("amount of coin outputs and output identifiers are not matching: {} != {}".format(len(transaction.coin_outputs), len(coinoutputids)), endpoint, resp)
        for (idx, id) in enumerate(coinoutputids):
            transaction.coin_outputs[idx].id = Hash.from_json(obj=id)
        # set the unconfirmed state
        transaction.unconfirmed = etxn.get('unconfirmed', False)
        # return the transaction
        return transaction

    def _explorer_get(self, endpoint):
        """
        Private utility method that gets the data on the given endpoint,
        but in a method so it can be overriden for Testing purposes.
        """
        return j.clients.tfchain.explorer.get(addresses=self.explorer_addresses, endpoint=endpoint)

    def _explorer_post(self, endpoint, data):
        """
        Private utility method that sets the data on the given endpoint,
        but in a method so it can be overriden for Testing purposes.
        """
        return j.clients.tfchain.explorer.post(addresses=self.explorer_addresses, endpoint=endpoint, data=data)

    def _normalize_unlockhash(self, unlockhash):
        if isinstance(unlockhash, UnlockHash):
            return str(unlockhash)

        if isinstance(unlockhash, (bytes, bytearray)):
            unlockhash = unlockhash.hex()
        elif isinstance(unlockhash, str):
            unlockhash = str(unlockhash)
        else:
            raise TypeError("Unlock hash has to be a string-like or Hash type")

        return str(UnlockHash.from_json(unlockhash))

    def _normalize_id(self, id):
        if isinstance(id, Hash):
            return str(id)
        id = Hash(value=id)
        return str(id)


class ExplorerBlockchainInfo():
    def __init__(self, last_block):
        self._last_block = last_block

    @property
    def last_block(self):
        """
        Last known block.
        """
        return self._last_block

    @property
    def blockid(self):
        """
        ID of last known block.
        """
        return str(self.last_block.id)
    
    @property
    def height(self):
        """
        Current height of the blockchain.
        """
        return self.last_block.height
    
    @property
    def timestamp(self):
        """
        The timestamp of the last registered block on the chain.
        """
        return self.last_block.timestamp

    def __repr__(self):
        return "Block {} at height {}, published on {}, is the last known block.".format(
            self.blockid, self.height, j.data.time.epoch2HRDateTime(self.timestamp))


class ExplorerUnlockhashResult():
    def __init__(self, unlockhash, transactions, multisig_addresses):
        """
        All the info found for a given unlock hash, as reported by an explorer.
        """
        self._unlockhash = unlockhash
        self._transactions = transactions
        self._multisig_addresses = multisig_addresses
    
    @property
    def unlockhash(self):
        """
        Unlock hash looked up.
        """
        return self._unlockhash
    
    @property
    def transactions(self):
        """
        Transactions linked to the looked up unlockhash.
        """
        return self._transactions

    @property
    def multisig_addresses(self):
        """
        Addresses of multisignature wallets co-owned by the looked up unlockhash.
        """
        return self._multisig_addresses

    def __repr__(self):
        return "Found {} transaction(s) and {} multisig address(es) for {}".format(
            len(self._transactions), len(self._multisig_addresses), str(self._unlockhash))


class ExplorerBlock():
    def __init__(self, id, parentid, height, timestamp, transactions, miner_payouts):
        """
        A Block, registered on a TF blockchain, as reported by an explorer.
        """
        self._id = id
        self._parentid = parentid
        self._height = height
        self._timestamp = timestamp
        self._transactions = transactions
        self._miner_payouts = miner_payouts
    
    @property
    def id(self):
        """
        Identifier of this block.
        """
        return str(self._id)

    @property
    def parentid(self):
        """
        Identifier the parent of this block.
        """
        return str(self._parentid)

    @property
    def height(self):
        """
        Height at which this block is registered.
        """
        return self._height

    @property
    def timestamp(self):
        """
        Timestamp on which this block is registered.
        """
        return self._timestamp

    @property
    def transactions(self):
        """
        Transactions that are included in this block.
        """
        return self._transactions

    @property
    def miner_payouts(self):
        """
        Miner payouts that are included in this block.
        """
        return self._miner_payouts
    
    def __str__(self):
        return str(self.id)
    __repr__ = __str__


class ExplorerMinerPayout():
    def __init__(self, id, value, unlockhash):
        """
        A single miner payout, as ereported by an explorer.
        """
        self._id = id
        self._value = value
        self._unlockhash = unlockhash

    @property
    def id(self):
        """
        Identifier of this miner payout.
        """
        return str(self._id)

    @property
    def value(self):
        """
        Value of this miner payout.
        """
        return self._value

    @property
    def unlockhash(self):
        """
        Unlock hash that received this miner payout's value.
        """
        return str(self._unlockhash)
    
    def __str__(self):
        return str(self.id)
    __repr__ = __str__
