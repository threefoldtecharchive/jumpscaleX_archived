"""
Client factory for the Tfchain network, js entry point
"""

from Jumpscale import j

import sys
import requests

from clients.blockchain.rivine import utils
from clients.blockchain.tfchain.TfchainClient import TfchainClient
from clients.blockchain.tfchain.TfchainNetwork import TfchainNetwork
from clients.blockchain.tfchain.errors import NoExplorerNetworkAddresses
from clients.blockchain.rivine.errors import RESTAPIError
from clients.blockchain.tfchain.TfchainThreeBotClient import TfchainThreeBotClient
from clients.blockchain.rivine.types.transaction import TransactionFactory
from clients.blockchain.rivine.types.transaction import TransactionFactory,\
        TransactionV128, TransactionV129, TransactionSummary, FlatMoneyTransaction
from clients.blockchain.rivine.types.unlockconditions import UnlockHashCondition,\
        LockTimeCondition, MultiSignatureCondition, UnlockCondtionFactory
from clients.blockchain.rivine.types.unlockhash import UnlockHash

from clients.blockchain.rivine.errors import WalletAlreadyExistsException

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class TfchainClientFactory(JSConfigBaseFactory):
    """
    Factory class to get a tfchain client object
    """
    __jslocation__ = "j.clients.tfchain"
    _CHILDCLASS = TfchainClient

    def _init(self):
        self.__imports__ = "tfchain"

    @property
    def network(self):
        return TfchainNetwork

    @property
    def threebot(self):
        return TfchainThreeBotClient

    def generate_seed(self):
        """
        Generates a new seed and returns it as a mnemonic
        """
        return j.data.encryption.mnemonic.generate(strength=256)


    def get_transaction(self, identifier, network=TfchainNetwork.STANDARD, explorers=None):
        """
        Get a transaction registered on a TFchain network

        @param identifier: unique transaction id in string hex-encoded format
        @param network: optional network, STANDARD by default, TESTNET is another valid choice, for DEVNET use the network_addresses param instead
        @param explorers: explorer network addresses from which to get the transaction (only required for DEVNET, optional for other networks)
        """
        # TODO: have a clean modular solution to get data from an explorer endpoint, instead of repeating it everywhere
        # TODO: we probably want to move to seperate clients for seperate networks, such that the clients are aware of their networks and explorers
        #       allowing you to do 'j.clients.tfchain.testnet.get_transaction', 'j.clients.tfchain.standard.get_transaction'
        #       as well as 'j.clients.tfchain.devnet(['localhost:23110']).get_transaction
        if not explorers:
            explorers = network.official_explorers()
            if not explorers:
                raise NoExplorerNetworkAddresses("network {} has no official explorer networks and none were specified by callee".format(network.name.lower()))

        msg = 'Failed to retrieve transaction.'
        result = None
        response = None
        for address in explorers:
            url = '{}/explorer/hashes/{}'.format(address.strip('/'), identifier)
            headers = {'user-agent': 'Rivine-Agent'}
            try:
                response = requests.get(url, headers=headers, timeout=10)
            except requests.exceptions.ConnectionError:
                continue
            if response.status_code == 200:
                result = response.json()
                break

        if result is None:
            if response:
                raise RESTAPIError('{} {}'.format(msg, response.text.strip('\n')))
            else:
                raise RESTAPIError('error while fetching transaction from {} for {}: {}'.format(explorers, identifier, msg))

        tx = result.get('transaction', {})
        if not tx:
            raise RESTAPIError('error while fetching transaction from {} for {}: transaction not found'.format(explorers, identifier))
        return TransactionSummary.from_explorer_transaction(tx)


    def list_incoming_transactions_for(self, addresses, network=TfchainNetwork.STANDARD, explorers=None, min_height=0):
        """
        Get all transactions for the given addresses as registered on a TFchain network

        @param addresses: addresses to look transactions for
        @param network: optional network, STANDARD by default, TESTNET is another valid choice, for DEVNET use the network_addresses param instead
        @param explorers: explorer network addresses from which to get the transaction (only required for DEVNET, optional for other networks)
        """
        # TODO: we probably want to move to seperate clients for seperate networks, such that the clients are aware of their networks and explorers
        #       allowing you to do 'j.clients.tfchain.testnet.get_transaction', 'j.clients.tfchain.standard.get_transaction'
        #       as well as 'j.clients.tfchain.devnet(['localhost:23110']).get_transaction
        if not explorers:
            explorers = network.official_explorers()
            if not explorers:
                raise NoExplorerNetworkAddresses("network {} has no official explorer networks and none were specified by callee".format(network.name.lower()))
        if not addresses:
            raise ValueError("no addresses given to look transactions for")
        
        # list all transactions
        # create the list where all found transaction summaries will be stored in
        transactions = []
        
        # list the transactions of all transactions, one by one
        for address in addresses:
            try:
                address_info = utils.check_address(explorers, address, min_height=min_height, log_errors=False)
            except RESTAPIError:
                pass
            else:
                address_transactions = address_info.get('transactions', {})
                if not address_transactions:
                    continue
                for tx in address_transactions:
                    transactions.extend([tx for tx in FlatMoneyTransaction.create_list(tx) if tx.to_address in addresses])
        
        # return all listed transactions, reverse-sorted by block height
        transactions.sort(key=lambda tx: tx.block_height if tx.confirmed else sys.maxsize, reverse=True)
        return transactions

    def create_transaction_from_json(self, txn_json):
        """
        Loads a transaction from a json string

        @param txn_json: Json string representing a transaction
        """
        return TransactionFactory.from_json(txn_json)


    def create_wallet(self, wallet_name, network = TfchainNetwork.STANDARD, seed = '', explorers = None, password = ''):
        """
        Creates a named wallet

        @param network : defines which network to use, use j.clients.tfchain.network.TESTNET for testnet
        @param seed : restores a wallet from a seed
        """
        if not explorers:
            explorers = []
        if self.exists(wallet_name):
            raise WalletAlreadyExistsException(wallet_name)
        data = {
            'network': network.name.lower(),
            'seed_': seed,
            'explorers': explorers,
            'password': password,
        }
        return self.get(wallet_name, data=data).wallet

    def open_wallet(self, wallet_name):
        """
        Opens a named wallet.
        Raises the j.exceptions.NotFound exception if the wallet is not found.
        """
        if not self.exists(wallet_name):
            raise j.exceptions.NotFound('No wallet found with name {}'.format(wallet_name))
        return self.get(wallet_name).wallet


    def create_minterdefinition_transaction(self, condition=None, description=None, network=TfchainNetwork.STANDARD):
        """
        Create a new minter definition transaction

        @param condition: Set the minter definition to this premade condition
        @param description: Add this description as arbitrary data to the transaction
        """
        tx = TransactionV128()
        tx.add_minerfee(network.minimum_minerfee())
        if condition is not None:
           tx.set_condition(condition)
        if description is not None:
            tx.set_data(description.encode('utf-8'), data_type=1)
        return tx

    def create_coincreation_transaction(self, amount=None, condition=None, description=None, network=TfchainNetwork.STANDARD):
        """
        Create a new coin creation transaction. If both an amount and condition are
        given, they will be used to create a first output in the transaction

        @param amount: The amount of coins to create for the condition, if given
        @param condition: A premade condition, used to create a first output
        @param description: A description which is added to the transaction as arbitrary data
        """
        tx = TransactionV129()
        tx.add_minerfee(network.minimum_minerfee())
        if amount is not None and condition is not None:
            tx.add_output(amount, condition)
        if description is not None:
            tx.set_data(description.encode('utf-8'), data_type=1)
        return tx

    def create_singlesig_condition(self, address, locktime=None):
        """
        Create a new single signature condition
        """
        unlockhash = UnlockHash.from_string(address)
        condition = UnlockHashCondition(unlockhash=unlockhash)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        return condition

    def create_multisig_condition(self, unlockhashes, min_nr_sig, locktime=None):
        """
        Create a new multisig condition
        """
        condition = MultiSignatureCondition(unlockhashes=unlockhashes, min_nr_sig=min_nr_sig)
        if locktime is not None:
            condition = LockTimeCondition(condition=condition, locktime=locktime)
        return condition
