
from Jumpscale import j

from functools import reduce

from ed25519 import SigningKey

from .types.PrimitiveTypes import Currency, Hash
from .types.CryptoTypes import PublicKey, UnlockHash, UnlockHashType
from .types.Errors import ExplorerNoContent, InsufficientFunds
from .types.CompositionTypes import CoinOutput, CoinInput
from .types.ConditionTypes import ConditionNil, ConditionUnlockHash, ConditionLockTime

from .TFChainTransactionFactory import TransactionBaseClass, TransactionV128, TransactionV129

_DEFAULT_KEY_SCAN_COUNT = 3

# TODO:
# * Make lock more user-friendly to be used (e.g. also accept durations and time strings)
# * Provide ERC20 Support
# * Provide Atomic Swap support
# * Provide 3Bot Registration (Management) Support

# TODO (TESTS, for now already manually tested and confirmed):
# * Send Coins (single sig and multi sig, with data and lock, as well as without)
# * Minter Transactions (single sig and multi sig)

class TFChainWallet(j.application.JSBaseConfigClass):
    """
    Tfchain Wallet object
    """
    _SCHEMATEXT = """
        @url = jumpscale.tfchain.wallet
        name* = "" (S)
        seed = "" (S)
        key_count = 1 (I)

        key_scan_count = -1 (I)
        """

    def _init(self):
        # stores all key pairs of this wallet in memory
        self._key_pairs = {}
        # the primary address is kept as a seperate property,
        # as we hint the user into using this primary address as much as possible,
        # to keep things simple
        self._primary_address = ''

        # when during scanning we find a used key,
        # it might happen that one or more keys prior the used keys are not used,
        # in this case we do want to increase the key_count,
        # but will keep the unused keys in a seperate bucket, so we
        # can use them first
        self._unused_key_pairs = []

        # cache balance so we only update when the block chain info changes
        self._cached_balance = None

        # provide sane defaults for the schema-based wallet config
        if self.seed == "":
            self.seed = j.data.encryption.mnemonic.generate(strength=256)
        if self.key_count < 1:
            self.key_count = 1

        # generate keys
        keys_to_generate = self.key_count
        self.key_count = 0
        # generate the primary address
        self._primary_address = str(self._key_pair_new().unlockhash)
        # generate the other addresses
        for _ in range(keys_to_generate-1):
            self._key_pair_new()

        # add sub-apis
        self._minter = TFChainMinter(wallet=self)
    
    @property
    def minter(self):
        """
        Minter used to update the (Coin) Minter Definition
        as well as to mint new coins, only useable if this wallet
        has (co-)ownership over the current (coin) minter definition.
        """
        return self._minter

    @property
    def client(self):
        """
        Returns the TFChain Client that owns this wallet,
        and through which this wallet communicates with Explorer nodes.
        """
        return self._parent._parent

    @property
    def network_type(self):
        """
        The network type, defined by the parent TFChain client,
        that this wallet is operating on.

        Changing the network type has to be done from the parent TFChain client.
        """
        return self.client.network

    @property
    def seed_entropy(self):
        """
        The entropy, based on the Wallet's seed,
        that is used to generate the public-private key pairs
        owned and used by this wallet.
        """
        return j.data.encryption.mnemonic.to_entropy(self.seed)

    @property
    def addresses(self):
        """
        The addresses owned and used by this wallet.
        """
        return list(self._key_pairs.keys())

    @property
    def address_count(self):
        """
        The amount of addresses owned and used by this wallet.
        """
        return len(self._key_pairs)

    @property
    def address(self):
        """
        The primary address, the address generated with index 0.
        """
        return self._primary_address

    @property
    def addresses_multisig(self):
        """
        The multi signature wallet addresses co-owned and linked to this wallet,
        as reported by the internal balance reporter.
        """
        balance = self.balance
        return list(balance.wallets.keys())

    @property
    def balance(self):
        """
        The balance "sheet" of the wallet.
        """
        # first get chain info, so we can check if the current balance is still fine
        info = self.client.blockchain_info_get()
        if self._cached_balance and self._cached_balance.chain_blockid == info.blockid:
            return self._cached_balance

        addresses = self.addresses
        balance = WalletsBalance()
        # collect info for all personal addresses
        multisig_addresses = []
        for address in addresses:
            try:
                # collect the inputs/outputs linked to this address for all found transactions
                result = self._unlockhash_get(address)
                for txn in result.transactions:
                    for ci in txn.coin_inputs:
                        if str(ci.parent_output.condition.unlockhash) == address:
                            balance.output_add(ci.parent_output, confirmed=(not txn.unconfirmed), spent=True)
                    for co in txn.coin_outputs:
                        if str(co.condition.unlockhash) == address:
                            balance.output_add(co, confirmed=(not txn.unconfirmed), spent=False)
                # collect all multisig addresses
                for address in result.multisig_addresses:
                    multisig_addresses.append(str(address))
            except ExplorerNoContent:
                 # ignore this exception as it simply means
                 # the address has no activity yet on the chain
                pass

        # try some extra key scanning, to see if other keys have been used
        # if we already have unsused keys, no scanning is done however
        if len(self._unused_key_pairs) == 0 and self.key_scan_count != 0:
            # use the defined count or the default one
            count = self.key_scan_count
            if count < 0:
                count = _DEFAULT_KEY_SCAN_COUNT
            # generate the key pairs, without integrating them already
            # loop, and do this until now more are found:
            while True:
                pairs = []
                used_pairs = []
                for offset in range(count):
                    pairs.append(self._key_pair_new(integrate=False, offset=offset))
                for pair in pairs:
                    address = str(pair.unlockhash)
                    try:
                        # collect the inputs/outputs linked to this address for all found transactions
                        result = self._unlockhash_get(address)
                        for txn in result.transactions:
                            for ci in txn.coin_inputs:
                                if str(ci.parent_output.condition.unlockhash) == address:
                                    balance.output_add(ci.parent_output, confirmed=(not txn.unconfirmed), spent=True)
                            for co in txn.coin_outputs:
                                if str(co.condition.unlockhash) == address:
                                    balance.output_add(co, confirmed=(not txn.unconfirmed), spent=False)
                        # register this pair as a known index
                        used_pairs.append(True)
                        # collect all multisig addresses
                        for address in result.multisig_addresses:
                            multisig_addresses.append(str(address))
                    except ExplorerNoContent:
                        # ignore this exception as it simply means
                        # the address has no activity yet on the chain
                        used_pairs.append(False)
                        pass
                # check if any address was found
                if not reduce(lambda a, b: a or b, used_pairs):
                    break

                last_index = 0
                for idx, pair in enumerate(pairs):
                    if used_pairs[idx]:
                        last_index = idx
                        self._key_pair_add(pair, add_count=False)
                    else:
                        self._unused_key_pairs.append(pair)
                # remove the unused pairs that came after the last known index
                self._unused_key_pairs = self._unused_key_pairs[:-count+last_index]
                # update the new key count
                self.key_count += last_index + 1

                # if the last pair is not used, we can stop scanning
                if not used_pairs[-1]:
                    break
                # otherwise continue

        # collect info for all multisig addresses
        for address in multisig_addresses:
            try:
                # collect the inputs/outputs linked to this address for all found transactions
                result = self._unlockhash_get(address)
                for txn in result.transactions:
                    for ci in txn.coin_inputs:
                        if str(ci.parent_output.condition.unlockhash) == address:
                            balance.multisig_output_add(address, ci.parent_output, confirmed=(not txn.unconfirmed), spent=True)
                    for co in txn.coin_outputs:
                        if str(co.condition.unlockhash) == address:
                            balance.multisig_output_add(address, co, confirmed=(not txn.unconfirmed), spent=False)
            except ExplorerNoContent:
                 # ignore this exception as it simply means
                 # the address has no activity yet on the chain
                pass
        # add the blockchain info for lock context
        balance.chain_height = info.height
        balance.chain_time = info.timestamp
        balance.chain_blockid = info.blockid
        # cache the balance
        self._cached_balance = balance
        # return the balance
        return balance

    def coins_send(self, recipient, amount, source=None, refund=None, lock=None, data=None):
        """
        Send the specified amount of coins to the given recipient,
        optionally locked. Arbitrary data can be attached as well if desired.

        The recipient is one of:
            - None: recipient is the Free-For-All wallet
            - str (or unlockhash): recipient is a personal wallet
            - list: recipient is a MultiSig wallet where all owners (specified as a list of addresses) have to sign
            - tuple (addresses, sigcount): recipient is a sigcount-of-addresscount MultiSig wallet

        The amount can be a str or an int:
            - when it is an int, you are defining the amount in the smallest unit (that is 1 == 0.000000001 TFT)
            - when defining as a str you can use the following space-stripped and case-insentive formats:
                - '123456789': same as when defining the amount as an int
                - '123.456': define the amount in TFT (that is '123.456' == 123.456 TFT == 123456000000)
                - '123456 TFT': define the amount in TFT (that is '123456 TFT' == 123456 TFT == 123456000000000)
                - '123.456 TFT': define the amount in TFT (that is '123.456 TFT' == 123.456 TFT == 123456000000)

        Returns (txn, submitted), with the second value of the pair indicating
        if this wallet has added any signatures in this call and the first
        pair value being the transaction created (and if possible submitted).
        
        @param recipient: see explanation above
        @param amount: int or str that defines the amount of TFT to set, see explanation above
        @param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        @param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        @param lock: optional lock that can be used to lock the sent amount to a specific time or block height
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        """
        amount = Currency(value=amount)
        if amount <= 0:
            raise ValueError("no amount is defined to be sent")

        # define recipient
        recipient = j.clients.tfchain.types.conditions.from_recipient(recipient, lock_time=lock)

        # fund amount
        balance = self.balance
        minerfee = self.client.minimum_minerfee
        inputs, remainder, suggested_refund = balance.fund(amount+minerfee, source=source)

        # define the refund condition
        if refund is None: # automatically choose a refund condition if none is given
            if suggested_refund is None:
                refund = j.clients.tfchain.types.conditions.unlockhash_new(unlockhash=self.address)
            else:
                refund = suggested_refund
        else:
            # use the given refund condition (defined as a recipient)
            refund = j.clients.tfchain.types.conditions.from_recipient(refund)

        # create transaction
        txn = j.clients.tfchain.transactions.new()
        # add main coin output
        txn.coin_output_add(value=amount, condition=recipient)
        # add refund coin output if needed
        if remainder > 0:
            txn.coin_output_add(value=remainder, condition=refund)
        # add the miner fee
        txn.miner_fee_add(minerfee)

        # add the coin inputs
        txn.coin_inputs = inputs
        
        # if there is data to be added, add it as well
        if data:
            txn.data = data

        # generate the signature requests
        sig_requests = txn.signature_requests_new()
        if len(sig_requests) == 0:
            raise Exception("BUG: sig requests should not be empty at this point, please fix or report as an issue")

        # fulfill the signature requests that we can fulfill
        for request in sig_requests:
            try:
                key_pair = self.key_pair_get(request.wallet_address)
                input_hash = request.input_hash_new(public_key=key_pair.public_key)
                signature = key_pair.sign(input_hash)
                request.signature_fulfill(public_key=key_pair.public_key, signature=signature)
            except KeyError:
                pass # this is acceptable due to how we directly try the key_pair_get method

        # txn should be fulfilled now
        submit = txn.is_fulfilled()
        if submit:
            # submit the transaction
            txn.id = self._transaction_put(transaction=txn)

            # update balance
            for ci in txn.coin_inputs:
                balance.output_add(ci.parent_output, confirmed=False, spent=True)
            addresses = self.addresses + list(balance.wallets.keys())
            for idx, co in enumerate(txn.coin_outputs):
                if str(co.condition.unlockhash) in addresses:
                    # add the id to the coin_output, so we can track it has been spent
                    co.id = txn.coin_outputid_new(idx)
                    balance.output_add(co, confirmed=False, spent=False)
            # and return the created/submitted transaction for optional user consumption

        return (txn, submit)

    def transaction_sign(self, txn, submit=True):
        """
        Sign in all places of the transaction where it is still possible,
        and on which the wallet has authority to do so.

        Returns (txn, signed, submitted), with the second value of the pair indicating
        if this wallet has added any signatures in this call and the first
        pair value being the (decoded) and up-to-date transaction value,
        and the third value indicating if this transaction was submitted.

        @param txn: transaction to sign, a JSON-encoded txn or already loaded in-memory as a valid Transaction type
        """
        # validate and/or normalize txn parameter
        if isinstance(txn, (str, dict)):
            txn = j.clients.tfchain.transactions.from_json(txn)
        elif not isinstance(txn, TransactionBaseClass):
            raise TypeError("txn value has invalid type {} and cannot be signed".format(type(txn)))

        balance = self.balance

        # check all parentids from the specified coin inputs,
        # and set the coin outputs for the ones this wallet knows about
        # and that are still unspent
        if len(txn.coin_inputs) > 0:
            # collect all known outputs
            known_outputs = {}
            for co in balance.outputs_available:
                known_outputs[co.id] = co
            for co in balance.outputs_unconfirmed_available:
                known_outputs[co.id] = co
            for wallet in balance.wallets.values():
                for co in wallet.outputs_available:
                    known_outputs[co.id] = co
                for co in wallet.outputs_unconfirmed_available:
                    known_outputs[co.id] = co
            # mark the coin inputs that are known as available outputs by this wallet
            for ci in txn.coin_inputs:
                if ci.parentid in known_outputs:
                    ci.parent_output = known_outputs[ci.parentid]

        # check for specific transaction types, as to
        # be able to add whatever content we know we can add
        if isinstance(txn, (TransactionV128, TransactionV129)):
            # set the parent mint condition
            txn.parent_mint_condition = self.client.mint_condition_get()
            # define the current fulfillment if it is not defined
            if not txn.mint_fulfillment_defined():
                txn.mint_fulfillment = j.clients.tfchain.types.fulfillments.from_condition(txn.parent_mint_condition)

        # generate the signature requests
        sig_requests = txn.signature_requests_new()
        if len(sig_requests) == 0:
            # possible if the wallet does not own any of the still required signatures,
            # or for example because the wallet does not know about the parent outputs of
            # the inputs still to be signed
            return (txn, False, False)

        # fulfill the signature requests that we can fulfill
        signature_count = 0
        for request in sig_requests:
            try:
                key_pair = self.key_pair_get(request.wallet_address)
                input_hash = request.input_hash_new(public_key=key_pair.public_key)
                signature = key_pair.sign(input_hash)
                request.signature_fulfill(public_key=key_pair.public_key, signature=signature)
                signature_count += 1
            except KeyError:
                pass # this is acceptable due to how we directly try the key_pair_get method

        # check if fulfilled, and if so, we'll submit unless the callee does not want that
        is_fulfilled = txn.is_fulfilled()
        submit = (submit and is_fulfilled)
        if submit:
            txn.id = self._transaction_put(transaction=txn)
            addresses = self.addresses + list(balance.wallets.keys())
            # update balance
            for ci in txn.coin_inputs:
                if str(ci.parent_output.condition.unlockhash) in addresses:
                    balance.output_add(ci.parent_output, confirmed=False, spent=True)
            for idx, co in enumerate(txn.coin_outputs):
                if str(co.condition.unlockhash) in addresses:
                    # add the id to the coin_output, so we can track it has been spent
                    co.id = txn.coin_outputid_new(idx)
                    balance.output_add(co, confirmed=False, spent=False)

        # return up-to-date Txn, as well as if we signed and submitted
        return (txn, (signature_count>0), submit)

    def address_new(self):
        """
        Generate a new wallet address,
        using the wallet's seed and the current key index as input.

        An address, also known as unlock hash,
        is a blake2 hash of the public key that is linked to a private key.
        The public key is used for verification of signatures,
        that were created with the matching private key.
        """
        return str(self._key_pair_new().unlockhash)

    def public_key_new(self):
        """
        Generate a new wallet public key,
        using the wallet's seed and the current key index as input.
        """
        return self._key_pair_new().public_key

    def key_pair_get(self, unlockhash):
        """
        Get the private/public key pair for the given unlock hash.
        If the unlock has is not owned by this wallet a KeyError exception is raised.
        """
        if not isinstance(unlockhash, (str, UnlockHash)):
            raise TypeError("unlockhash cannot be of type {}".format(type(unlockhash)))
        unlockhash = str(unlockhash)
        key = self._key_pairs.get(unlockhash)
        if key is None:
            raise KeyError("wallet does not own unlock hash {}".format(unlockhash))
        return key

    def _unlockhash_get(self, address):
        return self.client.unlockhash_get(address)

    def _transaction_put(self, transaction):
        return self.client.transaction_put(transaction)

    def _key_pair_new(self, integrate=True, offset=0):
        """
        Create a new key pair,
        and integrate it by default as well into the wallet's key pair dictionary.
        """
        # if we have unused key pairs in-memory, use them first,
        # only used when integrating is True,
        # as we do not wish to use this feature when scanning
        if integrate and len(self._unused_key_pairs) > 0:
            key_pair = self._unused_key_pairs.pop(0)
            self._key_pair_add(key_pair, add_count=False)
            return key_pair

        # otherwise create a new one
        e = j.data.rivine.encoder_sia_get()
        e.add_array(self.seed_entropy)
        e.add(self.key_count+offset)
        seed_hash = bytes.fromhex(j.data.hash.blake2_string(e.data))
        private_key = SigningKey(seed_hash)
        public_key = private_key.get_verifying_key()
        
        key_pair = SpendableKey(
            public_key = j.clients.tfchain.types.public_key_new(hash=public_key.to_bytes()),
            private_key = private_key)

        # if we wish to integrate (mostly when we're not scanning),
        # we also add it to our wallets known key pairs
        if integrate:
            self._key_pair_add(key_pair, add_count=True, offset=offset)

        return key_pair

    def _key_pair_add(self, key_pair, add_count=True, offset=0):
        """
        A private utility function that is used by default
        by the _key_pair_new wallet method to integrate a newly created key pair
        into this wallet's key pair dictionary.

        This method is seperate as we also scan for other keys during the fetching
        of the balance of a wallet. When we do, we want to create new key pairs,
        but only integrate them, if indeed we found the key (or a key after it) was used.
        """
        addr = str(key_pair.unlockhash)
        if addr in self._key_pairs:
            raise KeyError("wallet already contains a key pair for unlock hash {}".format(addr))
        self._key_pairs[addr] = key_pair
        if add_count:
            self.key_count += 1+offset
        # clear cache, as it will no longer be up to date
        self._clear_cache()

    def _clear_cache(self):
        self._cached_balance = None

from .types.ConditionTypes import ConditionMultiSignature
from .types.FulfillmentTypes import FulfillmentMultiSignature, PublicKeySignaturePair

class TFChainMinter():
    """
    TFChainMinter contains all Coin Minting logic.
    """

    def __init__(self, wallet):
        self._wallet = wallet

    def definition_set(self, minter, data=None):
        """
        Redefine the current minter definition.
        Arbitrary data can be attached as well if desired.

        The minter is one of:
            - str (or unlockhash): minter is a personal wallet
            - list: minter is a MultiSig wallet where all owners (specified as a list of addresses) have to sign
            - tuple (addresses, sigcount): minter is a sigcount-of-addresscount MultiSig wallet
        
        @param minter: see explanation above
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        """
        # create empty Mint Definition Txn, with a newly generated Nonce set already
        txn = j.clients.tfchain.transactions.mint_definition_new()

        # add the minimum miner fee
        txn.miner_fee_add(self._minium_miner_fee)

        # set the new mint condition
        txn.mint_condition = j.clients.tfchain.types.conditions.from_recipient(minter)

        # optionally set the data
        if data is not None:
            txn.data = data

        # get and set the current mint condition
        txn.parent_mint_condition = self._current_mint_condition_get()
        # create a raw fulfillment based on the current mint condition
        txn.mint_fulfillment = j.clients.tfchain.types.fulfillments.from_condition(txn.parent_mint_condition)

        # get all signature requests
        sig_requests = txn.signature_requests_new()
        if len(sig_requests) == 0:
            raise Exception("BUG: sig requests should not be empty at this point, please fix or report as an issue")

        # fulfill the signature requests that we can fulfill
        for request in sig_requests:
            try:
                key_pair = self._wallet.key_pair_get(request.wallet_address)
                input_hash = request.input_hash_new(public_key=key_pair.public_key)
                signature = key_pair.sign(input_hash)
                request.signature_fulfill(public_key=key_pair.public_key, signature=signature)
            except KeyError:
                pass # this is acceptable due to how we directly try the key_pair_get method

        submit = txn.is_fulfilled()
        if submit:
            txn.id = self._transaction_put(transaction=txn)

        # return the txn, as well as the submit status as a boolean
        return (txn, submit)

    def coins_new(self, recipient, amount, lock=None, data=None):
        """
        Create new (amount of) coins and give them to the defined recipient.
        Arbitrary data can be attached as well if desired.

        The recipient is one of:
            - None: recipient is the Free-For-All wallet
            - str (or unlockhash/bytes/bytearray): recipient is a personal wallet
            - list: recipient is a MultiSig wallet where all owners (specified as a list of addresses) have to sign
            - tuple (addresses, sigcount): recipient is a sigcount-of-addresscount MultiSig wallet

        The amount can be a str or an int:
            - when it is an int, you are defining the amount in the smallest unit (that is 1 == 0.000000001 TFT)
            - when defining as a str you can use the following space-stripped and case-insentive formats:
                - '123456789': same as when defining the amount as an int
                - '123.456': define the amount in TFT (that is '123.456' == 123.456 TFT == 123456000000)
                - '123456 TFT': define the amount in TFT (that is '123456 TFT' == 123456 TFT == 123456000000000)
                - '123.456 TFT': define the amount in TFT (that is '123.456 TFT' == 123.456 TFT == 123456000000)

        @param recipient: see explanation above
        @param amount: int or str that defines the amount of TFT to set, see explanation above
        @param lock: optional lock that can be used to lock the sent amount to a specific time or block height
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        """
        # create empty Mint Definition Txn, with a newly generated Nonce set already
        txn = j.clients.tfchain.transactions.mint_coin_creation_new()

        # add the minimum miner fee
        txn.miner_fee_add(self._minium_miner_fee)

        balance = self._wallet.balance

        # parse the output
        amount = Currency(value=amount)
        if amount <= 0:
            raise ValueError("no amount is defined to be sent")

        # define recipient
        recipient = j.clients.tfchain.types.conditions.from_recipient(recipient, lock_time=lock)
        # and add it is the output
        txn.coin_output_add(value=amount, condition=recipient)

        # optionally set the data
        if data is not None:
            txn.data = data

        # get and set the current mint condition
        txn.parent_mint_condition = self._current_mint_condition_get()
        # create a raw fulfillment based on the current mint condition
        txn.mint_fulfillment = j.clients.tfchain.types.fulfillments.from_condition(txn.parent_mint_condition)

        # get all signature requests
        sig_requests = txn.signature_requests_new()
        if len(sig_requests) == 0:
            raise Exception("BUG: sig requests should not be empty at this point, please fix or report as an issue")

        # fulfill the signature requests that we can fulfill
        for request in sig_requests:
            try:
                key_pair = self._wallet.key_pair_get(request.wallet_address)
                input_hash = request.input_hash_new(public_key=key_pair.public_key)
                signature = key_pair.sign(input_hash)
                request.signature_fulfill(public_key=key_pair.public_key, signature=signature)
            except KeyError:
                pass # this is acceptable due to how we directly try the key_pair_get method

        submit = txn.is_fulfilled()
        if submit:
            txn.id = self._transaction_put(transaction=txn)
            # update balance of wallet
            addresses = self._wallet.addresses + list(balance.wallets.keys())
            for idx, co in enumerate(txn.coin_outputs):
                if str(co.condition.unlockhash) in addresses:
                    # add the id to the coin_output, so we can track it has been spent
                    co.id = txn.coin_outputid_new(idx)
                    balance.output_add(co, confirmed=False, spent=False)

        # return the txn, as well as the submit status as a boolean
        return (txn, submit)

    @property
    def _minium_miner_fee(self):
        """
        Returns the minimum miner fee
        """
        return self._wallet.client.minimum_minerfee

    def _current_mint_condition_get(self):
        """
        Get the current mind condition from the parent TFChain client.
        """
        return self._wallet.client.mint_condition_get()

    def _transaction_put(self, transaction):
        """
        Submit the transaction to the network using the parent's wallet client.

        Returns the transaction ID.
        """
        return self._wallet._transaction_put(transaction=transaction)


class SpendableKey():
    """
    SpendableKey defines a PublicPrivate key pair as useable
    by a TFChain wallet.
    """

    def __init__(self, public_key, private_key):
        if not isinstance(public_key, PublicKey):
            raise TypeError("public key cannot be of type {} (expected: PublicKey)".format(type(public_key)))
        self._public_key = public_key
        if not isinstance(private_key, SigningKey):
            raise TypeError("private key cannot be of type {} (expected: SigningKey)".format(type(private_key)))
        self._private_key = private_key

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key(self):
        return self._private_key

    @property
    def unlockhash(self):
        return self._public_key.unlockhash()

    def sign(self, hash):
        """
        Sign the given hash and return the signature.

        @param hash: hash to be signed
        """
        if not isinstance(hash, Hash):
            hash = Hash(value=hash)
        hash = bytes(hash.value)
        return self._private_key.sign(hash)


class WalletBalance(object):
    def __init__(self):
        # personal wallet outputs
        self._outputs = {}
        self._outputs_spent = {}
        self._outputs_unconfirmed = {}
        self._outputs_unconfirmed_spent = {}
        # balance chain context
        self._chain_time = 0
        self._chain_height = 0
        self._chain_blockid = Hash()

    @property
    def chain_blockid(self):
        """
        Blockchain block ID, as defined by the last known block.
        """
        return self._chain_blockid
    @chain_blockid.setter
    def chain_blockid(self, value):
        """
        Set the blockchain block ID, such that applications that which to cache this
        balance object could ensure that the last block is still the same as the
        last known block known by this balance instance.
        """
        if not value:
            self._chain_blockid = Hash()
            return
        if isinstance(value, Hash):
            self._chain_blockid.value = value.value
        else:
            self._chain_blockid.value = value

    @property
    def chain_time(self):
        """
        Blockchain time, as defined by the last known block.
        """
        return self._chain_time
    @chain_time.setter
    def chain_time(self, value):
        """
        Set the blockchain time, such that the balance object can report
        locked/unlocked outputs correctly for outputs that are locked by time.
        """
        if not isinstance(value, int):
            raise TypeError("WalletBalance's chain time cannot be of type {} (expected: int)".format(type(value)))
        self._chain_time = int(value)

    @property
    def chain_height(self):
        """
        Blockchain height, as defined by the last known block.
        """
        return self._chain_height
    @chain_height.setter
    def chain_height(self, value):
        """
        Set the blockchain height, such that the balance object can report
        locked/unlocked outputs correctly for outputs that are locked by height.
        """
        if not isinstance(value, int):
            raise TypeError("WalletBalance's chain height cannot be of type {} (expected: int)".format(type(value)))
        self._chain_height = int(value)

    @property
    def active(self):
        """
        Returns if this balance is active,
        meaning it has available outputs to spend (confirmed or not).
        """
        return len(self._outputs) > 0 or len(self._outputs_unconfirmed) > 0

    @property
    def outputs_spent(self):
        """
        Spent (coin) outputs.
        """
        return self._outputs_spent
    @property
    def outputs_unconfirmed(self):
        """
        Unconfirmed (coin) outputs, available for spending or locked.
        """
        return self._outputs_unconfirmed
    @property
    def outputs_unconfirmed_available(self):
        """
        Unconfirmed (coin) outputs, available for spending.
        """
        if self.chain_time > 0 and self.chain_height > 0:
            return [co for co in self._outputs_unconfirmed.values()
                if not co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)]
        else:
            return list(self._outputs_unconfirmed.values())
    @property
    def outputs_unconfirmed_spent(self):
        """
        Unconfirmed (coin) outputs that have already been spent.
        """
        return self._outputs_unconfirmed_spent

    @property
    def outputs_available(self):
        """
        Total available (coin) outputs.
        """
        if self.chain_time > 0 and self.chain_height > 0:
            return [co for co in self._outputs.values()
                if not co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)]
        else:
            return list(self._outputs.values())

    @property
    def available(self):
        """
        Total available coins.
        """
        return sum([co.value for co in self.outputs_available]) or Currency()

    @property
    def locked(self):
        """
        Total available coins that are locked.
        """
        if self.chain_time > 0 and self.chain_height > 0:
            return sum([co.value for co in self._outputs.values()
                if co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)]) or Currency()
        else:
            return Currency(value=0) # impossible to know for sure without a complete context

    @property
    def unconfirmed(self):
        """
        Total unconfirmed coins, available for spending.
        """
        if self.chain_time > 0 and self.chain_height > 0:
            return sum([co.value for co in self._outputs_unconfirmed.values()
                if not co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)]) or Currency()
        else:
            return sum([co.value for co in self._outputs_unconfirmed.values()])

    @property
    def unconfirmed_locked(self):
        """
        Total unconfirmed coins that are locked, and thus not available for spending.
        """
        if self.chain_time > 0 and self.chain_height > 0:
            return sum([co.value for co in self._outputs_unconfirmed.values()
                if co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)]) or Currency()
        else:
            return Currency(value=0) # impossible to know for sure without a complete context

    def output_add(self, output, confirmed=True, spent=False):
        """
        Add an output to the Wallet's balance.
        """
        if confirmed: # confirmed outputs
            if spent:
                self._outputs_spent[output.id] = output
                # delete from other output lists if prior registered
                self._outputs.pop(output.id, None)
                self._outputs_unconfirmed.pop(output.id, None)
                self._outputs_unconfirmed_spent.pop(output.id, None)
            elif output.id not in self._outputs_spent and output.id not in self._outputs_unconfirmed_spent:
                self._outputs[output.id] = output
                # delete from other output lists if prior registered
                self._outputs_unconfirmed.pop(output.id, None)
        elif output.id not in self._outputs_spent: # unconfirmed outputs
            if spent:
                self._outputs_unconfirmed_spent[output.id] = output
                # delete from other output lists if prior registered
                self._outputs_unconfirmed.pop(output.id, None)
                self._outputs.pop(output.id, None)
            elif output.id not in self._outputs_unconfirmed_spent:
                self._outputs_unconfirmed[output.id] = output

    def _human_readable_balance(self):
        # report confirmed coins
        result = "{} available and {} locked".format(self.available.str(with_unit=True), self.locked.str(with_unit=True))
        # optionally report unconfirmed coins
        unconfirmed = self.unconfirmed
        unconfirmed_locked = self.unconfirmed_locked
        if unconfirmed > 0 or unconfirmed_locked > 0:
            result += "\nUnconfirmed: {} available {} locked".format(unconfirmed.str(with_unit=True), unconfirmed_locked.str(with_unit=True))
        unconfirmed_spent = Currency(value=sum([co.value for co in self._outputs_unconfirmed_spent.values()]))
        if unconfirmed_spent > 0:
            result += "\nUnconfirmed Balance Deduction: -{}".format(unconfirmed_spent.str(with_unit=True))
        # return report
        return result

    def __repr__(self):
        # report chain context
        result = ""
        if self.chain_height > 0 and self.chain_time > 0:
            result += "wallet balance on height {} at {}\n".format(self.chain_height, j.data.time.epoch2HRDateTime(self.chain_time))
        else:
            result += "wallet balance at an unknown time\n"
        # report context + balance
        return result + self._human_readable_balance()

from .types.ConditionTypes import ConditionMultiSignature

class MultiSigWalletBalance(WalletBalance):
    def __init__(self, owners, signature_count):
        """
        Creates a personal multi signature wallet.
        """
        if not isinstance(signature_count, int):
            raise TypeError("signature count of a MultiSigWallet is expected to be of type int, not {}".format(type(signature_count)))
        if signature_count < 1:
            raise ValueError("signature count of a MultiSigWallet has to be at least 1, cannot be {}".format(signature_count))
        if len(owners) < signature_count:
            raise ValueError("the amount of owners ({}) cannot be lower than the specified signature count ({})".format(len(owners), signature_count))
        self._owners = owners
        self._signature_count = signature_count
        super().__init__()

    @property
    def address(self):
        """
        The address of this MultiSig Wallet
        """
        return str(ConditionMultiSignature(unlockhashes=self._owners, min_nr_sig=self._signature_count).unlockhash)

    @property
    def owners(self):
        """
        Owners of this MultiSignature Wallet
        """
        return [str(owner) for owner in self._owners]

    @property
    def signature_count(self):
        """
        Amount of signatures minimum required
        """
        return self._signature_count

    def _human_readable_balance(self):
        result = "MultiSignature ({}-of-{}) Wallet {}:\n".format(self.signature_count, len(self.owners), self.address)
        result += "Owners: " + ", ".join(self.owners) +"\n"
        result += super()._human_readable_balance()
        return result

class WalletsBalance(WalletBalance):
    def __init__(self):
        """
        Creates a personal wallet, which also can have children wallets that are meant for
        all MultiSignature wallets that are related to one or more addresses of the personal wallet.
        """
        self._wallets = {}
        super().__init__()

    @property
    def wallets(self):
        """
        All multisig wallets linked to this wallet.
        """
        return self._wallets

    def multisig_output_add(self, address, output, confirmed=True, spent=False):
        """
        Add an output to the MultiSignature Wallet's balance.
        """
        oc = output.condition.unwrap()
        if not isinstance(oc, ConditionMultiSignature):
            raise TypeError("multi signature's output condition cannot be of type {} (expected: ConditionMultiSignature)".format(type(oc)))
        if not address in self._wallets:
            self._wallets[address] = MultiSigWalletBalance(
                owners=output.condition.unlockhashes,
                signature_count=output.condition.required_signatures)
        self._wallets[address].output_add(output, confirmed=confirmed, spent=spent)

    def output_add(self, output, confirmed=True, spent=False):
        """
        Add an output to the Wallet's balance.
        """
        uh = output.condition.unlockhash
        if uh.type == UnlockHashType.MULTI_SIG:
            return self.multisig_output_add(address=str(uh), output=output, confirmed=confirmed, spent=spent)
        return super().output_add(output=output, confirmed=confirmed, spent=spent)

    def __repr__(self):
        result = super().__repr__()
        for wallet in self.wallets.values():
            if wallet.active: # only display active wallets in the Human (shell) Representation
                result += "\n\n" + wallet._human_readable_balance()
        return result

    def fund(self, amount, source=None):
        """
        Fund the specified amount with the available outputs of this wallet's balance.
        """
        # collect addresses and multisig addresses
        addresses = set()
        ms_addresses = set()
        refund = None
        if source is None:
            for co in self.outputs_available:
                addresses.add(co.condition.unlockhash)
            for co in self.outputs_unconfirmed_available:
                addresses.add(co.condition.unlockhash)
        else:
            # if only one address is given, transform it into an acceptable list
            if not isinstance(source, list):
                if isinstance(source, str):
                    source = UnlockHash.from_json(source)
                elif not isinstance(source, UnlockHash):
                    raise TypeError("cannot add source address from type {}".format(type(source)))
                source = [source]
            # add one or multiple personal/multisig addresses
            for value in source:
                if isinstance(value, str):
                    value = UnlockHash.from_json(value)
                elif not isinstance(value, UnlockHash):
                    raise TypeError("cannot add source address from type {}".format(type(value)))
                if value.type == UnlockHashType.MULTI_SIG:
                    ms_addresses.add(value)
                elif value.type == UnlockHashType.PUBLIC_KEY:
                    addresses.add(value)
                else:
                    raise TypeError("cannot add source addres with unsupported UnlockHashType {}".format(value.type))
            if len(source) == 1:
                if source[0].type == UnlockHashType.PUBLIC_KEY:
                    refund = j.clients.tfchain.types.conditions.unlockhash_new(unlockhash=source[0])
                else:
                    addr = str(source[0])
                    if addr in self.wallets:
                        wallet = self.wallets[addr]
                        refund = j.clients.tfchain.types.conditions.multi_signature_new(min_nr_sig=wallet.signature_count, unlockhashes=wallet.owners)


        # ensure at least one address is defined
        if len(addresses) == 0 and len(ms_addresses) == 0:
            raise InsufficientFunds("no addresses defined or linked to this wallet")

        # if personal addresses are given, try to use these first
        # as these are the easiest kind to deal with
        if len(addresses) == 0:
            outputs, collected = ([], Currency()) # start with nothing
        else:
            outputs, collected = self._fund_individual(amount, addresses)

        if collected >= amount:
            # if we already have sufficient, we stop now
            return ([CoinInput.from_coin_output(co) for co in outputs], collected-amount, refund)

        if len(ms_addresses) == 0:
            # if no ms_addresses were defined,
            raise InsufficientFunds("not enough funds available in the individual wallet to fund the requested amount")
        # otherwise keep going for multisig addresses
        outputs, collected = self._fund_multisig(amount, ms_addresses, outputs=outputs, collected=collected)

        # if we still didn't manage to fund enough, there is nothing we can do
        if collected < amount:
            raise InsufficientFunds("not enough funds available in the wallets to fund the requested amount")
        return ([CoinInput.from_coin_output(co) for co in outputs], collected-amount, refund)

    def _fund_individual(self, amount, addresses):
        outputs_available = [co for co in self.outputs_available if co.condition.unlockhash in addresses]
        outputs_available.sort(key=lambda co: co.value)
        collected = Currency(value=0)
        outputs = []
        # try to fund only with confirmed outputs, if possible
        for co in outputs_available:
            if co.value >= amount:
                return [co], co.value
            collected += co.value
            outputs.append(co)
            if len(outputs) > 99:
                # to not reach the input limit
                collected -= outputs.pop(0).value
            if collected >= amount:
                return outputs, collected

        if collected >= amount:
            # if we already have sufficient, we stop now
            return outputs, collected

        # use unconfirmed balance, not ideal, but acceptable
        outputs_available = [co for co in self.outputs_unconfirmed_available if co.condition.unlockhash in addresses]
        outputs_available.sort(key=lambda co: co.value, reverse=True)
        for co in outputs_available:
            if co.value >= amount:
                return [co], co.value
            collected += co.value
            outputs.append(co)
            if len(outputs) > 99:
                # to not reach the input limit
                collected -= outputs.pop(0).value
            if collected >= amount:
                return outputs, collected

        # we return whatever we have collected, no matter if it is sufficient
        return outputs, collected

    def _fund_multisig(self, amount, addresses, outputs=None, collected=None):
        if outputs is None:
            outputs = []
        if collected is None:
            collected = Currency()
        for address, wallet in self.wallets.items():
            if UnlockHash.from_json(address) not in addresses:
                continue # nothing to do here

            outputs_available = wallet.outputs_available
            outputs_available.sort(key=lambda co: co.value)
            # try to fund only with confirmed outputs, if possible
            for co in outputs_available:
                if co.value >= amount:
                    return [co], co.value

                collected += co.value
                outputs.append(co)
                if len(outputs) > 99:
                    # to not reach the input limit
                    collected -= outputs.pop(0).value
                if collected >= amount:
                    return outputs, collected

            if collected >= amount:
                # if we already have sufficient, we stop now
                return outputs, collected

            # use unconfirmed balance, not ideal, but acceptable
            outputs_available = wallet.outputs_unconfirmed_available
            outputs_available.sort(key=lambda co: co.value, reverse=True)
            for co in outputs_available:
                if co.value >= amount:
                    return [co], co.value
                collected += co.value
                outputs.append(co)
                if len(outputs) > 99:
                    # to not reach the input limit
                    collected -= outputs.pop(0).value
                if collected >= amount:
                    return outputs, collected
        # we return whatever we have collected, no matter if it is sufficient
        return outputs, collected
