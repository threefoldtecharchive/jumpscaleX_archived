"""
Tfchain Client
"""

from Jumpscale import j
from .TFChainWalletFactory import TFChainWalletFactory
from .types.ConditionTypes import UnlockHash, UnlockHashType
from .types.PrimitiveTypes import Hash
from .types.CompositionTypes import CoinOutput

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
        'http://localhost:23112'
    ],
}


class TFChainClient(j.application.JSBaseConfigParentClass):
    """
    Tfchain client object
    """
    _SCHEMATEXT = """
        @url = jumpscale.tfchain.client
        name* = "" (S)
        network_type = "STD,TEST,DEV" (E)
        minimum_minerfee = 100000000 (I)
        explorer_nodes = (LO) !jumpscale.tfchain.explorer

        @url = jumpscale.tfchain.explorer
        address = "" (S)
        password = "" (S)
        """

    _CHILDCLASSES = [TFChainWalletFactory]

    def _data_trigger_new(self):
        if len(self.explorer_nodes) == 0:
            for address in _EXPLORER_NODES[self.network_type]:
                self.explorer_nodes.new().address = address
        if self.network_type == "DEV":
            self.minimum_minerfee = 1000000000
        else:
            self.minimum_minerfee = 100000000

    def transaction_get(self, txid):
        """
        Get a transaction from an available explorer Node.
        
        @param txid: the identifier (fixed string with a length of 64) that points to the desired transaction
        """
        txid = self._normalize_id(txid)
        resp = j.clients.tfchain.explorer.get(nodes=self.explorer_nodes.pylist(), endpoint="/explorer/hashes/"+txid)
        resp = data = j.data.serializers.json.loads(resp)
        assert resp['hashtype'] == 'transactionid'
        resp = resp['transaction']
        assert resp['id'] == txid
        return self._transaction_from_explorer_transaction(resp)
    
    def unlockhash_get(self, unlockhash):
        """
        Get all transactions linked to the given unlockhash,
        as well as other information such as the multisig addresses linked to the given unlockhash.

        @param unlockhash: the unlockhash to look up transactions for in the explorer
        """
        unlockhash = self._normalize_unlockhash(unlockhash)
        resp = j.clients.tfchain.explorer.get(nodes=self.explorer_nodes.pylist(), endpoint="/explorer/hashes/"+unlockhash)
        resp = data = j.data.serializers.json.loads(resp)
        assert resp['hashtype'] == 'unlockhash'
        # parse the transactions
        transactions = []
        for etxn in resp['transactions']:
            # parse the explorer transaction
            transaction = self._transaction_from_explorer_transaction(etxn)
            # append the transaction to the list of transactions
            transactions.append(transaction)
        # collect all multisig addresses
        multisig_addresses = [UnlockHash.from_json(obj=uh) for uh in etxn.get('multisigaddresses', [])]
        for addr in multisig_addresses:
            assert addr.type == UnlockHashType.MULTI_SIG
        # TODO: support etxn.get('erc20info')
        # return explorer data for the unlockhash
        return ExplorerUnlockhashResult(
            unlockhash=UnlockHash.from_json(unlockhash),
            transactions=transactions,
            multisig_addresses=multisig_addresses)
    
    def _transaction_from_explorer_transaction(self, etxn):
        # parse the transactions
        transaction = j.clients.tfchain.transactions.from_json(obj=etxn['rawtransaction'], id=etxn['id'])
        # add the parent (coin) outputs
        coininputoutputs = etxn.get('coininputoutputs', [])
        assert len(transaction.coin_inputs) == len(coininputoutputs)
        for (idx, co) in enumerate(coininputoutputs):
            transaction.coin_inputs[idx].parent_output = CoinOutput.from_json(obj=co)
        # add the coin output ids
        coinoutputids = etxn.get('coinoutputids', [])
        assert len(transaction.coin_outputs) == len(coinoutputids)
        for (idx, id) in enumerate(coinoutputids):
            transaction.coin_outputs[idx].id = Hash.from_json(obj=id)
        # set the unconfirmed state
        transaction.unconfirmed = etxn.get('unconfirmed', False)
        # return the transaction
        return transaction

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
