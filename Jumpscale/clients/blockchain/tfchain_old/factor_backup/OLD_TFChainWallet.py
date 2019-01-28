"""
This module implements a light weight wallet for Rivine blockchain network.
the wallet will need the following functionality:

- Starting from a seed, be able to derive the public and private keypairs.
- Use the public keys to create unlockcondition objects, which can be hashed to get the addresses.
- These addresses can be used to query the explorer to get the coininputs
- Remove those that are already spent
- When creating the transaction, select the coin inputs to have equal or more coins than the required output + minerfee. Change can be written back to one of your own addresses. Note that an input must be consumed in its entirety.
- For every public key in the input, the corresponding private key is required to sign the transaction to be valid
"""

import ed25519
import sys
from datetime import datetime

from .types.signatures import Ed25519PublicKey, SPECIFIER_SIZE
from .types.unlockhash import UnlockHash, UNLOCK_TYPE_PUBKEY, UNLOCKHASH_SIZE, UNLOCKHASH_CHECKSUM_SIZE

from Jumpscale import j
from clients.blockchain.rivine import utils, txutils
from clients.blockchain.rivine.atomicswap.atomicswap import AtomicSwapManager
from clients.blockchain.rivine.types.transaction import TransactionFactory,\
        DEFAULT_TRANSACTION_VERSION, CoinOutput, DEFAULT_MINERFEE, sign_bot_transaction, FlatMoneyTransaction
from clients.blockchain.rivine.types.unlockhash import UnlockHash
from clients.blockchain.rivine.types.unlockconditions import UnlockCondtionFactory,\
        MULTISIG_CONDITION_TYPE, MultiSignatureFulfillment, SingleSignatureFulfillment

from clients.blockchain.tfchain.TfchainThreeBotClient import TfchainThreeBotClient
from clients.blockchain.tfchain.types import signatures as tftsig

from .const import MINER_PAYOUT_MATURITY_WINDOW, WALLET_ADDRESS_TYPE, ADDRESS_TYPE_SIZE, HASTINGS_TFT_VALUE, UNLOCKHASH_TYPE,\
        NR_OF_EXTRA_ADDRESSES_TO_CHECK

from .errors import RESTAPIError, BackendError,\
InsufficientWalletFundsError, NonExistingOutputError,\
NotEnoughSignaturesFound, InvalidUnlockHashChecksumError


class TFChainWallet:
    """
    Wallet class
    """
    def __init__(self, seed, bc_networks, bc_network_password, nr_keys_per_seed=50, minerfee=100000000, client=None):
        """
        Creates new wallet
        TODO: check if we need to support multiple seeds from the begining

        @param seed: Starting point seed to generate keys.
        @param bc_networks: List of blockchain networks to use.
        @param bc_network_password: Password to send to the explorer node when posting requests.
        @param nr_keys_per_seed: Number of keys generated from the seed.
        @param minerfee: Amount of hastings that should be minerfee (default to 0.1 TFT)
        @param client: Client instance
        """
        self._client = client
        self._seed = j.data.encryption.mnemonic.to_entropy(seed)
        self._unspent_coin_outputs = {}
        self._locked_coin_outputs = {}
        self._unconfirmed_unspent_coin_outputs = {}
        self._unconfirmed_locked_coin_outputs = {}
        self._unconfirmed_unspent_multisig_outputs = {}
        self._unconfirmed_locked_multisig_outputs = {}
        self._multisig_wallets = set()
        self._unspent_multisig_outputs = {}
        self._locked_multisig_outputs = {}
        self._keys = {}
        self._bc_networks = bc_networks
        self._minerfee = minerfee
        self._bc_network_password = bc_network_password
        self._nr_keys_per_seed = nr_keys_per_seed
        for index in range(self._nr_keys_per_seed):
            key = self._generate_spendable_key(index=index)
            self._keys[str(key.unlockhash)] = key
        self._addresses_info = {}
        self.atomicswap = AtomicSwapManager(wallet=self)

    @property
    def seed(self):
        """
        Retrieves the current seed of the wallet
        """
        return j.data.encryption.mnemonic.to_mnemonic(self._seed)

    @property
    def addresses(self):
        """
        Wallet addresses to recieve and send funds
        """
        return [str(key) for key in self._keys.keys()]


    @property
    def current_balance(self):
        """
        Retrieves current wallet balance
        """
        self._check_balance()
        wb = WalletBalance()
        for id, output in self._unspent_coin_outputs.items():
            wb.add_unlocked_output(id, output)
        for id, output in self._locked_coin_outputs.items():
            wb.add_locked_output(id, output)
        for id, output in self._unspent_multisig_outputs.items():
            wb.add_unlocked_multisig_output(id, output)
        for id, output in self._locked_multisig_outputs.items():
            wb.add_locked_multisig_output(id, output)
        for id, output in self._unconfirmed_unspent_coin_outputs.items():
            wb.add_unconfirmed_unlocked_output(id, output)
        for id, output in self._unconfirmed_locked_coin_outputs.items():
            wb.add_unconfirmed_locked_output(id, output)
        for id, output in self._unconfirmed_unspent_multisig_outputs.items():
            wb.add_unconfirmed_unlocked_multisig_output(id, output)
        for id, output in self._unconfirmed_locked_multisig_outputs.items():
            wb.add_unconfirmed_locked_multisig_output(id, output)
        return wb

    def generate_key(self, persist=True):
        """
        Generates a new public key (and wallet address), returning the key
        """
        key = self._generate_spendable_key(index=self._nr_keys_per_seed)
        self._keys[str(key.unlockhash)] = key
        self._nr_keys_per_seed += 1
        if persist is True:
            self._save_nr_of_keys()
        return key

    def generate_address(self, persist=True):
        """
        Generates a new wallet address
        """
        return str(self.generate_key(persist=persist).unlockhash)

    def list_incoming_transactions(self, addresses=None, min_height=0):
        """
        List all incoming transactions related to a wallet,
        optionally filtering to only show the given address(es).
        """
        # create the list where all found transaction summaries will be stored in
        transactions = []

        # define the addresses to look for
        if not addresses:
            addresses = self.addresses
        else:
            addresses = list(set(addresses) & set(self.addresses))
        if not addresses:
            raise ValueError("there are no addresses to list transactions for")
        
        # list the transactions of all transactions, one by one
        for address in addresses:
            try:
                address_info = self._check_address(address=address, min_height=min_height, log_errors=False)
            except RESTAPIError:
                pass
            else:
                address_transactions = address_info.get('transactions', {})
                if not address_transactions:
                    continue
                for tx in address_transactions:
                    # collect all transactions
                    address_txs = FlatMoneyTransaction.create_list(tx)
                    inc_txs = [tx for tx in address_txs if tx.to_address in addresses]
                    inc_txs = [tx for tx in inc_txs if not(len(tx.from_addresses) == 1 and tx.from_addresses[0] == tx.to_address)]
                    transactions.extend(inc_txs)

        # return all listed transactions, reverse-sorted by block height
        transactions.sort(key=lambda tx: tx.block_height if tx.confirmed else sys.maxsize, reverse=True)
        return transactions

    def _save_nr_of_keys(self):
        """
        Saves the current number of keys in the client configurations
        """
        if self._client is not None:
            # we need to update the config with the new nr_of_keys_per_seed for this wallet
            data = dict(self._client.config.data)
            data['nr_keys_per_seed'] = self._nr_keys_per_seed
            client_factory = getattr(j.clients, self._client.__jslocation__.split('.')[-1])
            cl = client_factory.get(instance=self._client.instance,
                                    data=data,
                                    create=True,
                                    interactive=False)
            cl.config.save()

    def _generate_spendable_key(self, index):
        """
        Generate a @Spendablekey object from the seed and index

        @param index: Index of key to generate from the seed
        """
        binary_seed = bytearray()
        binary_seed.extend(binary.encode(self._seed))
        binary_seed.extend(binary.encode(index))
        binary_seed_hash = utils.hash(binary_seed)
        sk = ed25519.SigningKey(binary_seed_hash)
        pk = sk.get_verifying_key()
        return SpendableKey(pub_key=pk.to_bytes(), sec_key=sk)


    def _get_current_chain_height(self):
        """
        Retrieves the current chain height
        """
        return utils.get_current_chain_height(self._bc_networks)


    def _check_address(self, address, min_height=0, log_errors=True):
        """
        Check if an address is valid
        performs a http call to an explorer to check if an address has (an) (unspent) output(s)

        @param address: Address to check
        @param log_errors: If False, no logging will be executed

        @raises: @RESTAPIError if failed to check address
        """
        return utils.check_address(self._bc_networks, address, min_height=min_height, log_errors=log_errors)


    def _check_balance(self):
        """
        Syncs the wallet with the blockchain

        @TOCHECK: this needs to be synchronized with locks or other primitive
        """
        # Start by clearing any (possibly outdated info)
        self._addressis_info = {}
        current_chain_height = self._get_current_chain_height()
        logger.info('Current chain height is: {}'.format(current_chain_height))
        # remove unconfirmed outputs from prior iteration
        self._unconfirmed_unspent_coin_outputs = {}
        self._unconfirmed_locked_coin_outputs = {}
        self._unconfirmed_unspent_multisig_outputs = {}
        self._unconfirmed_locked_multisig_outputs = {}
        # when checking the balance we will check for 10 more addresses
        nr_of_addresses_to_check = self._nr_keys_per_seed + NR_OF_EXTRA_ADDRESSES_TO_CHECK
        for address_idx in range(nr_of_addresses_to_check):
            new_address = False
            addresses = self.addresses
            if address_idx < self._nr_keys_per_seed and address_idx < len(addresses):
                address = addresses[address_idx]
            else:
                address = str(self._generate_spendable_key(index=address_idx).unlockhash)
                new_address = True
            try:
                address_info = self._check_address(address=address, log_errors=False)
            except RESTAPIError:
                pass
            else:
                if new_address is True:
                    self._nr_keys_per_seed = address_idx + 1
                    self._save_nr_of_keys()

                # It could be that we found an address which is only part of a multisig
                # output. In that case some properties we depend on below won't be
                # available, but there will also not be an error. So collect the
                # multisig addresses first to query them later
                if address_info.get('multisigaddresses', []) is not None:
                    for ms_address in address_info.get('multisigaddresses', []):
                        self._multisig_wallets.add(ms_address)
                if address_info.get('transactions', {}) is None:
                    # address was only part of a multisig output, ignore the rest
                    continue
                if address_info.get('hashtype', None) != UNLOCKHASH_TYPE:
                    raise BackendError('Address is not recognized as an unlock hash')
                self._addresses_info[address] = address_info
                self._collect_miner_fees(address=address, blocks=address_info.get('blocks',{}),
                                        height=current_chain_height)
                transactions = address_info.get('transactions', {})
                self._collect_transaction_outputs(current_height=current_chain_height,
                                                  address=address,
                                                  transactions=transactions)
        # Add multisig addresses
        for address in self._multisig_wallets:
            try:
                address_info = self._check_address(address=address, log_errors=False)
            except RESTAPIError:
                pass
            else:
                if address_info.get('hashtype', None) != UNLOCKHASH_TYPE:
                    raise BackendError('Address is not recognized as an unlock hash')
                self._addresses_info[address] = address_info
                # Multisigs can't have minerfees currently
                transactions = address_info.get('transactions', {})
                self._collect_transaction_outputs(current_height=current_chain_height,
                                                    address=address,
                                                    transactions=transactions)

        # remove spent inputs after collection all the inputs
        for address, address_info in self._addresses_info.items():
            self._remove_spent_inputs(transactions = address_info.get('transactions', {}))


    def _collect_miner_fees(self, address, blocks, height):
        """
        Scan the bocks for miner fees and Collects the miner fees But only that have matured already

        @param address: address to collect miner fees for
        @param blocks: Blocks from an address
        @param height: The current chain height
        """
        self._unspent_coin_outputs.update(txutils.collect_miner_fees(address, blocks, height))


    def _collect_transaction_outputs(self, current_height, address, transactions):
        """
        Collects transactions outputs

        @param current_height: Current chain height
        @param address: address to collect transactions outputs
        @param transactions: Details about the transactions
        @param unconfirmed_txs: List of unconfirmed transactions
        """
        # split transactions into confirmed adn unconfirmed
        confirmed_tx = []
        unconfirmed_txs = []
        for tx in transactions:
            unconfirmed = tx.get('unconfirmed', False)
            if unconfirmed:
                unconfirmed_txs.append(tx)
            else:
                confirmed_tx.append(tx)
        txn_outputs = txutils.collect_transaction_outputs(current_height, address, confirmed_tx, unconfirmed_txs)
        self._unspent_coin_outputs.update(txn_outputs['unlocked'])
        self._locked_coin_outputs.update(txn_outputs['locked'])
        self._unspent_multisig_outputs.update(txn_outputs['multisig_unlocked'])
        self._locked_multisig_outputs.update(txn_outputs['multisig_locked'])
        self._unconfirmed_unspent_coin_outputs.update(txn_outputs['unconfirmed_unlocked'])
        self._unconfirmed_locked_coin_outputs.update(txn_outputs['unconfirmed_locked'])
        self._unconfirmed_unspent_multisig_outputs.update(txn_outputs['unconfirmed_multisig_unlocked'])
        self._unconfirmed_locked_multisig_outputs.update(txn_outputs['unconfirmed_multisig_locked'])


    def _remove_spent_inputs(self, transactions):
        """
        Remvoes the already spent outputs

        @param transactions: Details about the transactions
        """
        utils.remove_spent_inputs(self._unspent_coin_outputs, transactions)
        utils.remove_spent_inputs(self._unspent_multisig_outputs, transactions)
        utils.remove_spent_inputs(self._unconfirmed_unspent_coin_outputs, transactions)
        utils.remove_spent_inputs(self._unconfirmed_unspent_multisig_outputs, transactions)


    def _get_unconfirmed_transactions(self, format_inputs=False):
        """
        Retrieves the unconfirmed transaction from a remote node that runs the Transaction pool module

        @param format_inputs: If True, the output will be formated to get a list of the inputs parent ids

        # example output
                {'transactions': [{'version': 1,
           'data': {'coininputs': [{'parentid': '7616c88f452d6b22a3683bcbdfdf6ee3c32b63a810a8ac0d46a7403a33d4c06f',
              'fulfillment': {'type': 1,
               'data': {'publickey': 'ed25519:9413b12a6158f52fad6c39cc164054a9e7fbe5378892311f498eae56f80c068a',
                'signature': '34cee9bbc380deba2f52ccb20c2a47d4f6001fe66cfe7079d6b71367ea14544e89e69657201d0cc7b7b901324e64a7f4dce6ac6177536726cee576a0b74a8700'}}}],
            'coinoutputs': [{'value': '2000000000',
              'condition': {'type': 1,
               'data': {'unlockhash': '0112a7c1813746c5f6d5d496441d7a6a226984a3cc318021ee82b5695e4470f160c6ca61f66df2'}}},
             {'value': '3600000000',
              'condition': {'type': 1,
               'data': {'unlockhash': '012bdb563a4b3b630ddf32f1fde8d97466376a67c0bc9a278c2fa8c8bd760d4dcb4b9564cdea6f'}}}],
            'minerfees': ['100000000']}}]}
        """
        return utils.get_unconfirmed_transactions(self._bc_networks, format_inputs=format_inputs)


    def send_money(self, amount, recipient, data=None, data_type=0, locktime=None):
        """
        Sends TFT tokens from the user's wallet to the recipient address

        @param amount: Amount to be transfered in TF tokens
        @param recipient: Address of the fund recipient
        @param data: Custom data to be sent with the transaction
        @param locktime: Identifies the height or timestamp until which this transaction is locked
        """
        if data is not None:
            data = binary.encode(data)
        # convert amount to hastings
        amount = int(amount * HASTINGS_TFT_VALUE)
        transaction = self._create_transaction(amount=amount,
                                                recipient=recipient,
                                                sign_transaction=True,
                                                data=data,
                                                data_type=data_type,
                                                locktime=locktime)
        self._commit_transaction(transaction=transaction)
        return transaction


    def send_to_multisig(self, amount, recipients, required_nr_of_signatures, data=None, data_type=0, locktime=None):
        """
        Sends funds to multiple recipients
        Also specificies how many recipients need to sign before the funds can be spent

        @param amount: The amount needed to be transfered in TF Tokens
        @param recipients: List of recipients addresses.
        @param required_nr_of_signatures: Defines the amount of signatures required in order to spend this fund.
        @param data: Custom data to add to the transaction record
        @type custom_data: bytearray
        @param locktime: Identifies the height or timestamp until which this transaction is locked
        """

        if data is not None:
            data = binary.encode(data)
        # convert amount to hastings
        amount = int(amount * HASTINGS_TFT_VALUE)
        transaction = self._create_multisig_transaction(amount=amount,
                                                        recipients=recipients,
                                                        min_nr_sig=required_nr_of_signatures,
                                                        sign_transaction=True,
                                                        data=data,
                                                        data_type=data_type,
                                                        locktime=locktime)
        self._commit_transaction(transaction=transaction)
        return transaction

    def create_multisig_spending_transaction(self, *inputids, recipient=None, amount=None,
                                             refund_condition=None, locktime=None):
        """
        Create a new transactions which spends the multisig. If
        insufficient value is available in the given inputs, more inputs will need
        to be added on the transaction object manually.

        @param inputids: a number of multisig parentids which are not timelocked and part of the wallet
        @param recipient: the address of the receiver
        @param amoiunt: the amount of coins to send to the receiver
        @param refund_condition: the condition used in the refund. If enough inputs are given
            and this is not provided, the first input's condition will be used automatically
            if the input is more then required
        @param locktime: An optional locktime until which the output is locked
        """
        # Check if there are multisig inputs available. if not, try to get the balance,
        # might be that this function has not been called yet.
        if not self._unspent_multisig_outputs:
            _ = self.current_balance
        # Convert amount from one coin to the base unit
        if amount is not None:
            amount = amount * HASTINGS_TFT_VALUE
        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)
        if recipient is not None and amount is not None:
            transaction.add_coin_output(amount, recipient, locktime)
        # Track the total amount of input funds
        total_input = 0
        for inputid in inputids:
            # We want to create a transactions which spends the given multisig
            # outputs, so we only need to loop over the unlocked multisigs
            if not inputid in self._unspent_multisig_outputs:
                raise RuntimeError("Trying to spend multisig output which does not exist or is not unlocked yet")
            output = CoinOutput.from_dict(self._unspent_multisig_outputs[inputid])
            total_input += output._value
            transaction.add_multisig_input(inputid)
            # If no refund_condition is given take the condition from the first input we spend
            # just in case it would be needed
            if refund_condition is None:
                refund_condition = output._condition
        refund = 0
        if amount is not None and total_input > amount + DEFAULT_MINERFEE:
            refund = total_input - (amount + DEFAULT_MINERFEE)
        if refund > 0 and refund_condition is not None:
            transaction._coin_outputs.append(CoinOutput(value=refund, condition=refund_condition))
        transaction.add_minerfee(DEFAULT_MINERFEE)
        return transaction

    def _get_inputs(self, amount, minerfee=None):
        """
        Retrieves the inputs data that can cover the specified amount

        @param amount: The amount of funds that needs to be covered

        @returns: a tuple of (input info dictionary, the used addresses, minerfee, remainder)
        """
        if minerfee is None:
            minerfee = self._minerfee
        wallet_fund = int(self.current_balance.unlocked_unconfirmed_balance * HASTINGS_TFT_VALUE)
        required_funds = amount + minerfee
        if required_funds > wallet_fund:
            raise InsufficientWalletFundsError('No sufficient funds to make the transaction')

        result = []
        input_value = 0
        used_addresses = {}
        for address, unspent_coin_output in self._unspent_coin_outputs.items():
            # if we reach the required funds, then break
            if input_value >= required_funds:
                break
            input_result = {}
            ulh = self._get_unlockhash_from_output(output=unspent_coin_output, address=address)

            if not ulh:
                raise RuntimeError('Cannot retrieve unlockhash')

            # used_addresses.append(ulh)
            used_addresses[address] = ulh
            input_result['parent_id'] = address
            input_result['pub_key'] = self._keys[ulh].public_key

            input_value += int(unspent_coin_output['value'])
            result.append(input_result)
        if input_value < required_funds:
            for address, unspent_coin_output in self._unconfirmed_unspent_coin_outputs.items():
                # if we reach the required funds, then break
                if input_value >= required_funds:
                    break
                input_result = {}
                ulh = self._get_unlockhash_from_output(output=unspent_coin_output, address=address)

                if not ulh:
                    raise RuntimeError('Cannot retrieve unlockhash')

                # used_addresses.append(ulh)
                used_addresses[address] = ulh
                input_result['parent_id'] = address
                input_result['pub_key'] = self._keys[ulh].public_key

                input_value += int(unspent_coin_output['value'])
                result.append(input_result)
        return result, used_addresses, minerfee, (input_value - required_funds)


    def _create_multisig_transaction(self, amount, recipients, min_nr_sig=None, minerfee=None, sign_transaction=True, data=None, data_type=0, locktime=None):
        """
        Creates a transaction with Mulitsignature condition
        MultiSignature Condition allows the funds to be sent to multiple wallet addresses and specify how many signatures required to make this transaction spendable

        @param amount: The amount needed to be transfered in hastings
        @param recipients: List of recipients addresses.
        @param min_nr_sig: Defines the amount of signatures required in order to spend this output
        @param minerfee: The minerfee for this transaction in hastings
        @param sign_transaction: If True, the created transaction will be singed
        @param custom_data: Custom data to add to the transaction record
        @type custom_data: bytearray
        @param locktime: Identifies the height or timestamp until which this transaction is locked
        """
        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)

        # set the the custom data on the transaction
        if data is not None:
            transaction.set_data(data, data_type=data_type)


        input_results, used_addresses, minerfee, remainder = self._get_inputs(amount=amount)
        for input_result in input_results:
            transaction.add_coin_input(**input_result)

        for txn_input in transaction.coin_inputs:
            if used_addresses[txn_input.parent_id] not in self._keys:
            # if self._unspent_coin_outputs[txn_input.parent_id][ulh] not in self._keys:
                raise NonExistingOutputError('Trying to spend unexisting output')

        transaction.add_multisig_output(value=amount, unlockhashes=recipients, min_nr_sig=min_nr_sig, locktime=locktime)

        # we need to check if the sum of the inputs is more than the required fund and if so, we need
        # to send the remainder back to the original user
        if remainder > 0:
            # we have leftover fund, so we create new transaction, and pick on user key that is not used
            for address in self._keys.keys():
                if address in used_addresses.values():
                    continue
                transaction.add_coin_output(value=remainder, recipient=address)
                break

        # add minerfee to the transaction
        transaction.add_minerfee(minerfee)

        if sign_transaction:
            # sign the transaction
            self._sign_transaction(transaction)

        return transaction


    def _create_transaction(self, amount, recipient, minerfee=None, sign_transaction=True, data=None, data_type=0, locktime=None):
        """
        Creates new transaction and sign it
        creates a new transaction of the specified ammount to a specified address. A remainder address
        to which the leftover coins will be transfered (if any) is chosen automatically. An error is returned if the coins
        available in the coininputs are insufficient to cover the amount specified for transfer (+ the miner fee).

        @param amount: The amount needed to be transfered in hastings
        @param recipient: Address of the recipient.
        @param minerfee: The minerfee for this transaction in hastings
        @param sign_transaction: If True, the created transaction will be singed
        @param custom_data: Custom data to add to the transaction record
        @type custom_data: bytearray
        @param locktime: Identifies the height or timestamp until which this transaction is locked
        """
        transaction = TransactionFactory.create_transaction(version=DEFAULT_TRANSACTION_VERSION)

        # set the the custom data on the transaction
        if data is not None:
            transaction.set_data(data, data_type=data_type)


        input_results, used_addresses, minerfee, remainder = self._get_inputs(amount=amount)
        for input_result in input_results:
            transaction.add_coin_input(**input_result)

        for txn_input in transaction.coin_inputs:
            if used_addresses[txn_input.parent_id] not in self._keys:
            # if self._unspent_coin_outputs[txn_input.parent_id][ulh] not in self._keys:
                raise NonExistingOutputError('Trying to spend unexisting output')

        transaction.add_coin_output(value=amount, recipient=recipient, locktime=locktime)

        # we need to check if the sum of the inputs is more than the required fund and if so, we need
        # to send the remainder back to the original user
        if remainder > 0:
            # we have leftover fund, so we create new transaction, and pick on user key that is not used
            if self.addresses:
                transaction.add_coin_output(value=remainder, recipient=self.addresses[0])

        # add minerfee to the transaction
        transaction.add_minerfee(minerfee)

        if sign_transaction:
            # sign the transaction
            self._sign_transaction(transaction)

        return transaction


    def _get_unlockhash_from_output(self, output, address):
        """
        Retrieves unlockhash from coin output. This should handle different types of output conditions and transaction formats
        """
        ulh = txutils.get_unlockhash_from_output(output, address, current_height=self._get_current_chain_height())
        return ulh['unlocked'][0] if ulh['unlocked'] else None


    def _sign_transaction(self, transaction):
        """
        Signs a transaction with the existing keys.

        @param transaction: Transaction object to be signed
        """
        logger.info("Signing Transaction")
        for index, input in enumerate(transaction.coin_inputs):
            if input.parent_id in self._unspent_coin_outputs:
                #@TODO improve the parsing of outputs its duplicated now in too many places
                ulh = self._get_unlockhash_from_output(output=self._unspent_coin_outputs[input.parent_id], address=input.parent_id)
                if ulh in self._keys:
                    key = self._keys[ulh]
                    input.sign(input_idx=index, transaction=transaction, secret_key=key.secret_key)
                else:
                    logger.warn("Failed to retrieve unlockhash related to input {}".format(input))
                continue
            if input.parent_id in self._unconfirmed_unspent_coin_outputs:
                #@TODO improve the parsing of outputs its duplicated now in too many places
                ulh = self._get_unlockhash_from_output(output=self._unconfirmed_unspent_coin_outputs[input.parent_id], address=input.parent_id)
                if ulh in self._keys:
                    key = self._keys[ulh]
                    input.sign(input_idx=index, transaction=transaction, secret_key=key.secret_key)
                else:
                    logger.warn("Failed to retrieve unlockhash related to unconfirmed input {}".format(input))


    def _commit_transaction(self, transaction):
        """
        Commits a singed transaction to the chain

        @param transaction: Transaction object to be committed
        """
        return utils.commit_transaction(self._bc_networks, self._bc_network_password, transaction)


    def get_current_minter_definition(self):
        """
        Get the current minter definition
        """
        return utils.get_current_minter_definition(self._bc_networks, self._bc_network_password)

    def sign_transaction(self, transaction, multisig=False, commit=False):
        """
        Signs a transaction and optionally push it to the blockchain

        @param transaction: Transaction object
        @param multisig: If true, it indicates that the transaction contains multisig inputs.
        Only required for v1 transaction
        @param commit: If True, the transaction will be pushed to the chain after being signed
        """
        if transaction.version == 1:
            self._sign(transaction, multisig=multisig, commit=commit)
        elif transaction.version == 128 or transaction.version == 129:
            self._sign_mint_transaction(transaction, commit=commit)
        elif transaction.version == 144:
            self._sign_bot_registration_transaction(transaction, commit=commit)
        elif transaction.version == 145:
            self._sign_bot_record_update_transaction(transaction, commit=commit)
        elif transaction.version == 146:
            self._sign_bot_name_transfer_transaction(transaction, commit=commit)
        else:
            raise RuntimeError("Can't sign unknown transaction version")

    def _sign(self, transaction, multisig=False, commit=False):
        """
        Signs a transaction and optionally push it to the blockchain

        @param transaction: Transaction object
        @param multisig: If True, it indicates that the transaction contains multisig inputs
        @param commit: If True, the transaction will be pushed to the chain after being signed
        """
        if not multisig:
            self._sign_transaction(transaction=transaction)
        else:
            current_height = self._get_current_chain_height()
            for index, ci in enumerate(transaction.coin_inputs):
                output_info = self._check_address(ci._parent_id)
                for txn_info in output_info['transactions']:
                    for co in txn_info['rawtransaction']['data']['coinoutputs']:
                        ulhs = txutils.get_unlockhash_from_output(output=co,
                                                                address=ci._parent_id,
                                                                current_height=current_height)
                        ulh = list(set(self.addresses).intersection(ulhs['unlocked']))
                        if ulh:
                            ulh = ulh[0]
                            key = self._keys[ulh]
                            ci.sign(input_idx=index, transaction=transaction, secret_key=key.secret_key)
                        else:
                            logger.warn("Failed to retrieve unlockhash related to input {}".format(ci._parent_id))

        if commit:
            self._commit_transaction(transaction=transaction)

        return transaction


    def _sign_mint_transaction(self, transaction, commit=False):
        """
        Signs a minter definition or coin creation transaction and optionally push it to the chain
        @param transaction: A transactionV128 or transactionV129 object to sign
        @param commit: if True, the transaction will be pushed after signing
        """
        muc = UnlockCondtionFactory.from_dict(self.get_current_minter_definition())
        if muc.type == MULTISIG_CONDITION_TYPE:
            if transaction.mint_fulfillment is None:
                transaction._mint_fulfillment = MultiSignatureFulfillment()
            ulhs = list(set(self.addresses).intersection(muc._unlockhashes))
            for ulh in ulhs:
                key = self._keys[ulh]
                ctx = {
                    'secret_key': key.secret_key,
                    'input_idx': 0,
                    'transaction': transaction
                }
                transaction.mint_fulfillment.sign(ctx)
        else:
            if transaction.mint_fulfillment is None:
                transaction._mint_fulfillment = SingleSignatureFulfillment(None)
            if not muc._unlockhash in self._keys:
                return
            key = self._keys[muc._unlockhash]
            ctx = {
                'secret_key': key.secret_key,
                'input_idx': 0,
                'transaction': transaction
            }
            transaction.mint_fulfillment.sign(ctx)
        if commit:
            self._commit_transaction(transaction=transaction)

    def _sign_bot_registration_transaction(self, transaction, commit=False):
        """
        Signs a bot registration transaction and optionally push it to the chain
        @param transaction: A transactionV144 object to sign
        @param commit: if True, the transaction will be pushed after signing
        """
        # sign coin inputs
        self._sign(transaction, commit=False) # but do not commit (yet)
        # sign bot registration
        uh = str(transaction.identification.public_key.unlock_hash)
        if uh not in self._keys:
            logger.warn("no key found in wallet for unlock hash {}".format(uh))
            return
        key = self._keys[uh]
        transaction.identification.signature = sign_bot_transaction(transaction, transaction.identification.public_key, key.secret_key)
        if commit:
            self._commit_transaction(transaction=transaction)

    def _sign_bot_record_update_transaction(self, transaction, commit=False):
        """
        Signs a bot record update transaction and optionally push it to the chain
        @param transaction: A transactionV145 object to sign
        @param commit: if True, the transaction will be pushed after signing
        """
        # sign coin inputs
        self._sign(transaction, commit=False) # but do not commit (yet)
        # sign bot record update
        public_key = self._get_public_key_from_bot_id(transaction.get_bot_id())
        uh = str(public_key.unlock_hash)
        if uh not in self._keys:
            logger.warn("no key found in wallet for unlock hash {}".format(uh))
            return
        key = self._keys[uh]
        transaction.set_signature(sign_bot_transaction(transaction, public_key, key.secret_key))
        if commit:
            self._commit_transaction(transaction=transaction)

    def _sign_bot_name_transfer_transaction(self, transaction, commit=False):
        """
        Signs a bot name transfer transaction and optionally push it to the chain
        @param transaction: A transactionV146 object to sign
        @param commit: if True, the transaction will be pushed after signing
        """
        # sign coin inputs
        self._sign(transaction, commit=False) # but do not commit (yet)
        # sign bot record update as sender (if possible)
        sender_pub_key = self._get_public_key_from_bot_id(transaction.get_sender_bot_id())
        uh = str(sender_pub_key.unlock_hash)
        bots_signed = 0
        if uh in self._keys:
            bots_signed += 1
            key = self._keys[uh]
            transaction.set_sender_signature(sign_bot_transaction(transaction, sender_pub_key, key.secret_key))
        # sign bot record update as receiver (if possible)
        receiver_pub_key = self._get_public_key_from_bot_id(transaction.get_receiver_bot_id())
        uh = str(receiver_pub_key.unlock_hash)
        if uh in self._keys:
            bots_signed += 1
            key = self._keys[uh]
            transaction.set_receiver_signature(sign_bot_transaction(transaction, receiver_pub_key, key.secret_key))
        # commit if desired
        if commit and bots_signed == 2:
            self._commit_transaction(transaction=transaction)

    def _get_public_key_from_bot_id(self, identifier):
        record = TfchainThreeBotClient.get_record(identifier, self._bc_networks)
        return record.public_key
    
class SpendableKey:
    """
    SpendableKey is a secret signing key and its public verifying key
    """
    def __init__(self, pub_key, sec_key):
        """
        Creates new SpendableKey

        @param pub_key: A 32-bytes verifying key
        @param sec_key: A signing key that correspond to the verifying key
        """
        self._sk = sec_key
        self._pk = pub_key
        self._unlockhash = None

    @property
    def public_key(self):
        """
        Return the public verification key
        """
        return self._pk

    @property
    def secret_key(self):
        """
        Returns the secret key
        """
        return self._sk

    @property
    def unlockhash(self):
        """
        Calculate unlock hash of the spendable key
        """
        pub_key = Ed25519PublicKey(pub_key=self._pk)
        encoded_pub_key = binary.encode(pub_key)
        hash = utils.hash(encoded_pub_key, encoding_type='slice')
        return UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash)

class WalletBalance:
    """
    WalletBalance holds the locked and unlocked outputs in a wallet.
    """
    def __init__(self):
        self._unlocked_outputs = {}
        self._locked_outputs = {}
        self._unlocked_multisig_outputs = {}
        self._locked_multisig_outputs = {}
        self._unconfirmed_unlocked_outputs = {}
        self._unconfirmed_locked_outputs = {}
        self._unconfirmed_unlocked_multisig_outputs = {}
        self._unconfirmed_locked_multisig_outputs = {}

    def __str__(self):
        unlocked_value = sum(int(value.get('value', 0)) for value in self._unlocked_outputs.values()) / HASTINGS_TFT_VALUE
        string = 'Unlocked:\n\n\t{}\n'.format(unlocked_value)

        if len(self._unconfirmed_unlocked_outputs) > 0:
            unlocked_unconfirmed_value = sum(int(value.get('value', 0)) for value in self._unconfirmed_unlocked_outputs.values()) / HASTINGS_TFT_VALUE
            string += '\n\nUnconfirmed balance:\n\n\t{}\n'.format(unlocked_unconfirmed_value)

        if len(self._locked_outputs) > 0:
            string += '\nLocked:\n'
        for output in self._locked_outputs.values():
            string += '\n\t{} locked until {}\n'.format(int(output[0]['value']) / HASTINGS_TFT_VALUE,
                                                      self._locktime_to_string(output[1]))

        if len(self._unconfirmed_locked_outputs) > 0:
            string += '\nLocked (Unconfirmed):\n'
        for output in self._unconfirmed_locked_outputs.values():
            string += '\n\t{} locked until {}\n'.format(int(output[0]['value']) / HASTINGS_TFT_VALUE,
                                                      self._locktime_to_string(output[1]))

        if len(self._unlocked_multisig_outputs) > 0:
            string += '\nUnlocked multisig outputs:\n'
        for output_id, output in self._unlocked_multisig_outputs.items():
            string += '\n\tOutput id: {}\n'.format(output_id)
            if 'condition' in output:
                string += '\tSignature addresses:\n'
                for uh in output['condition']['data']['unlockhashes']:
                    string += '\t\t{}\n'.format(uh)
                string += '\tMinimum amount of signatures: {}\n'.format(output['condition']['data']['minimumsignaturecount'])
            elif 'unlockhash' in output:
                string += '\tMultisig Wallet Address: {}\n'.format(output['unlockhash'])
            string += '\tValue: {}\n'.format(int(output['value']) / HASTINGS_TFT_VALUE)

        if len(self._unconfirmed_unlocked_multisig_outputs) > 0:
            string += '\nUnlocked multisig outputs (unconfirmed):\n'
        for output_id, output in self._unconfirmed_unlocked_multisig_outputs.items():
            string += '\n\tOutput id: {}\n'.format(output_id)
            string += '\tSignature addresses:\n'
            for uh in output['condition']['data']['unlockhashes']:
                string += '\t\t{}\n'.format(uh)
            string += '\tMinimum amount of signatures: {}\n'.format(output['condition']['data']['minimumsignaturecount'])
            string += '\tValue: {}\n'.format(int(output['value']) / HASTINGS_TFT_VALUE)

        if len(self._locked_multisig_outputs) > 0:
            string += '\nLocked multisig outputs:\n'
        for output_id, output in self._locked_multisig_outputs.items():
            string += '\n\tOutput id: {}\n'.format(output_id)
            string += '\tSignature addresses:\n'
            for uh in output[0]['condition']['data']['unlockhashes']:
                string += '\t\t{}\n'.format(uh)
            string += '\tMinimum amount of signatures: {}\n'.format(output[0]['condition']['data']['minimumsignaturecount'])
            string += '\tValue: {} locked until {}\n'.format(int(output[0]['value']) / HASTINGS_TFT_VALUE,
                                                             self._locktime_to_string(output[1]))

        if len(self._unconfirmed_locked_multisig_outputs) > 0:
            string += '\nLocked multisig outputs (unconfirmed):\n'
        for output_id, output in self._locked_multisig_outputs.items():
            string += '\n\tOutput id: {}\n'.format(output_id)
            string += '\tSignature addresses:\n'
            for uh in output[0]['condition']['data']['unlockhashes']:
                string += '\t\t{}\n'.format(uh)
            string += '\tMinimum amount of signatures: {}\n'.format(output[0]['condition']['data']['minimumsignaturecount'])
            string += '\tValue: {} locked until {}\n'.format(int(output[0]['value']) / HASTINGS_TFT_VALUE,
                                                             self._locktime_to_string(output[1]))

        return string

    def __repr__(self):
        """
        Override so we have nice output in js shell if the object is not assigned
        without having to call the print method.
        """
        return str(self)

    @property
    def unlocked_balance(self):
        return sum(int(value.get('value', 0)) for value in self._unlocked_outputs.values()) / HASTINGS_TFT_VALUE

    @property
    def unlocked_unconfirmed_balance(self):
        return self.unlocked_balance + sum(int(value.get('value', 0)) for value in self._unconfirmed_unlocked_outputs.values()) / HASTINGS_TFT_VALUE

    @property
    def unlocked_outputs(self):
        return self._unlocked_outputs

    @property
    def locked_outputs(self):
        """
        Returns the currently locked outputs

        @returns dict, keys are the parent ids of the outputs, values are a tuple of the
        raw output. First tuple element is the raw output, second element is the
        locktime.
        """
        return self._locked_outputs

    def add_unlocked_output(self, output_id, raw_output):
        # It coudl be that this is a timelock condition which has expired
        if 'condition' in raw_output and raw_output['condition']['type'] == 3:
            raw_output['condition'] = raw_output['condition']['data']['condition']
        self._unlocked_outputs[output_id] = raw_output

    def add_unlocked_multisig_output(self, output_id, raw_output):
        # It could be that this is a timelock condition which has expired
        if 'condition' in raw_output and raw_output['condition']['type'] == 3:
            raw_output['condition'] = raw_output['condition']['data']['condition']
        self._unlocked_multisig_outputs[output_id] = raw_output

    def add_locked_output(self, output_id, raw_output):
        # Get the locktime
        locktime = raw_output['condition']['data']['locktime']
        # strip lock condition
        raw_output['condition'] = raw_output['condition']['data']['condition']
        self._locked_outputs[output_id] = (raw_output, locktime)

    def add_locked_multisig_output(self, output_id, raw_output):
        # Get the locktime
        locktime = raw_output['condition']['data']['locktime']
        # strip lock condition
        raw_output['condition'] = raw_output['condition']['data']['condition']
        self._locked_multisig_outputs[output_id] = (raw_output, locktime)

    def add_unconfirmed_unlocked_output(self, output_id, raw_output):
        # It coudl be that this is a timelock condition which has expired
        if 'condition' in raw_output and raw_output['condition']['type'] == 3:
            raw_output['condition'] = raw_output['condition']['data']['condition']
        self._unconfirmed_unlocked_outputs[output_id] = raw_output

    def add_unconfirmed_unlocked_multisig_output(self, output_id, raw_output):
        # It could be that this is a timelock condition which has expired
        if 'condition' in raw_output and raw_output['condition']['type'] == 3:
            raw_output['condition'] = raw_output['condition']['data']['condition']
        self._unconfirmed_unlocked_multisig_outputs[output_id] = raw_output

    def add_unconfirmed_locked_output(self, output_id, raw_output):
        # Get the locktime
        locktime = raw_output['condition']['data']['locktime']
        # strip lock condition
        raw_output['condition'] = raw_output['condition']['data']['condition']
        self._unconfirmed_locked_outputs[output_id] = (raw_output, locktime)

    def add_unconfirmed_locked_multisig_output(self, output_id, raw_output):
        # Get the locktime
        locktime = raw_output['condition']['data']['locktime']
        # strip lock condition
        raw_output['condition'] = raw_output['condition']['data']['condition']
        self._unconfirmed_locked_multisig_outputs[output_id] = (raw_output, locktime)

    def _locktime_to_string(self, locktime):
        # make sure we are working with an integer
        locktime = int(locktime)
        if locktime < 500000000:
            return "block " + str(locktime)
        ts = datetime.fromtimestamp(locktime)
        return ts.strftime("%Y-%m-%d %H:%M:%S")
