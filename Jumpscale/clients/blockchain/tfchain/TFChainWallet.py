
from Jumpscale import j

from functools import reduce

import hashlib
from ed25519 import SigningKey

from .types.PrimitiveTypes import Currency, Hash, BinaryData
from .types.CryptoTypes import PublicKey, UnlockHash, UnlockHashType
from .types.IO import CoinOutput, CoinInput
from .types.ConditionTypes import ConditionNil, ConditionUnlockHash, ConditionLockTime
from .types.AtomicSwap import AtomicSwapContract
from .types.ERC20 import ERC20Address
from .types.transactions.Base import TransactionBaseClass
from .types.transactions.Minting import TransactionV128, TransactionV129

_DEFAULT_KEY_SCAN_COUNT = 3

_MAX_RIVINE_TRANSACTION_INPUTS = 99

# TODO:
# add support for transaction listing (need to work this out)

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
        self._atomicswap = TFChainAtomicSwap(wallet=self)
        self._threebot = TFChainThreeBot(wallet=self)
        self._erc20 = TFChainERC20(wallet=self)

        # scan already for keys once
        self._key_scan()
    
    @property
    def minter(self):
        """
        Minter used to update the (Coin) Minter Definition
        as well as to mint new coins, only useable if this wallet
        has (co-)ownership over the current (coin) minter definition.
        """
        return self._minter

    @property
    def atomicswap(self):
        """
        Atomic Swap API used to create atomic swap contracts as initiator or participator,
        as well as to redeem and refund existing unredeemed atomic swap contrats.
        """
        return self._atomicswap

    @property
    def threebot(self):
        """
        ThreeBot API used to register new 3Bots and
        manage existing 3Bot records.
        """
        return self._threebot

    @property
    def erc20(self):
        """
        ERC20 API used to send coins to ERC20 Addresses,
        and register TFT addresses that can than be used as ERC20 Withdraw addresses.
        """
        return self._erc20

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
        return balance.addresses_multisig

    @property
    def balance(self):
        """
        The balance "sheet" of the wallet.
        """
        # key scan first
        scanned_new_keys = self._key_scan()

        # first get chain info, so we can check if the current balance is still fine
        info = self.client.blockchain_info_get()
        if not scanned_new_keys and self._cached_balance and self._cached_balance.chain_blockid == info.blockid:
            return self._cached_balance

        addresses = self.addresses
        balance = WalletsBalance()
        # collect info for all personal addresses
        multisig_addresses = []
        for address in addresses:
            try:
                # collect the inputs/outputs linked to this address for all found transactions
                result = self._unlockhash_get(address)
                uh_balance = result.balance(info=info)
                balance = balance.balance_add(uh_balance)
                # collect all multisig addresses
                for address in result.multisig_addresses:
                    multisig_addresses.append(str(address))
            except j.clients.tfchain.errors.ExplorerNoContent:
                 # ignore this exception as it simply means
                 # the address has no activity yet on the chain
                pass

        # collect info for all multisig addresses
        for address in multisig_addresses:
            try:
                # collect the inputs/outputs linked to this address for all found transactions
                result = self._unlockhash_get(address)
                uh_balance = result.balance(info=info)
                balance = balance.balance_add(uh_balance)
            except j.clients.tfchain.errors.ExplorerNoContent:
                 # ignore this exception as it simply means
                 # the address has no activity yet on the chain
                pass
        # ensure info is defined for wallet, even if no content
        balance.chain_blockid = info.blockid
        balance.chain_time = info.timestamp
        balance.chain_height = info.height
        # cache the balance
        self._cached_balance = balance
        # return the balance
        return balance

    def _key_scan(self):
        # try some extra key scanning, to see if other keys have been used
        # if we already have unsused keys, no scanning is done however
        if len(self._unused_key_pairs) != 0 or self.key_scan_count == 0:
            return False
    
        # use the defined count or the default one
        count = self.key_scan_count
        if count < 0:
            count = _DEFAULT_KEY_SCAN_COUNT
        # key track of start key count, so we can easily check at the end,
        # if we indeed scanned for any new keys
        key_count_start = self.key_count
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
                    self._unlockhash_get(address)
                    # register this pair as a known index
                    used_pairs.append(True)
                except j.clients.tfchain.errors.ExplorerNoContent:
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
        
        # return if we scanned new keys
        return self.key_count > key_count_start

    def coins_send(self, recipient, amount, source=None, refund=None, lock=None, data=None):
        """
        Send the specified amount of coins to the given recipient,
        optionally locked. Arbitrary data can be attached as well if desired.

        If the given recipient is a valid ERC20 address, than this will send
        the specified amount to that ERC20 address and no lock or data is allowed to be defined.

        The recipient is one of:
            - None: recipient is the Free-For-All wallet
            - str (or unlockhash): recipient is a personal wallet
            - list: recipient is a MultiSig wallet where all owners (specified as a list of addresses) have to sign
            - tuple (addresses, sigcount): recipient is a sigcount-of-addresscount MultiSig wallet
            - an ERC20 address (str/ERC20Address), amount will be send to this ERC20 address

        The amount can be a str or an int:
            - when it is an int, you are defining the amount in the smallest unit (that is 1 == 0.000000001 TFT)
            - when defining as a str you can use the following space-stripped and case-insentive formats:
                - '123456789': same as when defining the amount as an int
                - '123.456': define the amount in TFT (that is '123.456' == 123.456 TFT == 123456000000)
                - '123456 TFT': define the amount in TFT (that is '123456 TFT' == 123456 TFT == 123456000000000)
                - '123.456 TFT': define the amount in TFT (that is '123.456 TFT' == 123.456 TFT == 123456000000)

        The lock can be a str, or int:
            - when it is an int it represents either a block height or an epoch timestamp (in seconds)
            - when a str it can be a Jumpscale Datetime (e.g. '12:00:10', '31/10/2012 12:30', ...) or a Jumpscale Duration (e.g. '+ 2h', '+7d12h', ...)

        Returns a TransactionSendResult.
        
        @param recipient: see explanation above
        @param amount: int or str that defines the amount of TFT to set, see explanation above
        @param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        @param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        @param lock: optional lock that can be used to lock the sent amount to a specific time or block height, see explation above
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        """
        if ERC20Address.is_valid_value(recipient):
            if lock is not None:
                raise ValueError("a lock cannot be applied when sending coins to an ERC20 Address")
            if data is not None:
                raise ValueError("data cannot be added to the transaction when sending coins to an ERC20 Address")
            # all good, try to send to the ERC20 address
            return self.erc20.coins_send(address=recipient, amount=amount, source=source, refund=refund)

        amount = Currency(value=amount)
        if amount <= 0:
            raise ValueError("no amount is defined to be sent")

        # define recipient
        recipient = j.clients.tfchain.types.conditions.from_recipient(recipient, lock=lock)

        # fund amount
        balance = self.balance
        miner_fee = self.client.minimum_miner_fee
        inputs, remainder, suggested_refund = balance.fund(amount+miner_fee, source=source)

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
        txn = j.clients.tfchain.types.transactions.new()
        # add main coin output
        txn.coin_output_add(value=amount, condition=recipient)
        # add refund coin output if needed
        if remainder > 0:
            txn.coin_output_add(value=remainder, condition=refund)
        # add the miner fee
        txn.miner_fee_add(miner_fee)

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
            addresses = self.addresses + balance.addresses_multisig
            for idx, co in enumerate(txn.coin_outputs):
                if str(co.condition.unlockhash) in addresses:
                    # add the id to the coin_output, so we can track it has been spent
                    co.id = txn.coin_outputid_new(idx)
                    balance.output_add(co, confirmed=False, spent=False)
            # and return the created/submitted transaction for optional user consumption

        return TransactionSendResult(txn, submit)

    def transaction_sign(self, txn, submit=True):
        """
        Sign in all places of the transaction where it is still possible,
        and on which the wallet has authority to do so.

        Returns a TransactionSignResult.

        @param txn: transaction to sign, a JSON-encoded txn or already loaded in-memory as a valid Transaction type
        """
        # validate and/or normalize txn parameter
        if isinstance(txn, (str, dict)):
            txn = j.clients.tfchain.types.transactions.from_json(txn)
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
            txn.parent_mint_condition = self.client.minter.condition_get()
            # define the current fulfillment if it is not defined
            if not txn.mint_fulfillment_defined():
                txn.mint_fulfillment = j.clients.tfchain.types.fulfillments.from_condition(txn.parent_mint_condition)

        # generate the signature requests
        sig_requests = txn.signature_requests_new()
        if len(sig_requests) == 0:
            # possible if the wallet does not own any of the still required signatures,
            # or for example because the wallet does not know about the parent outputs of
            # the inputs still to be signed
            return TransactionSignResult(txn, False, False)

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
            addresses = self.addresses + balance.addresses_multisig
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
        return TransactionSignResult(txn, (signature_count>0), submit)

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
        if unlockhash[:2] == '00':
            key = self._key_pairs.get(self.address)
        else:
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
        if not isinstance(wallet, TFChainWallet):
            raise TypeError("wallet is expected to be a TFChainWallet")
        self._wallet = wallet

    def definition_set(self, minter, data=None):
        """
        Redefine the current minter definition.
        Arbitrary data can be attached as well if desired.

        The minter is one of:
            - str (or unlockhash): minter is a personal wallet
            - list: minter is a MultiSig wallet where all owners (specified as a list of addresses) have to sign
            - tuple (addresses, sigcount): minter is a sigcount-of-addresscount MultiSig wallet

        Returns a TransactionSendResult.
        
        @param minter: see explanation above
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        """
        # create empty Mint Definition Txn, with a newly generated Nonce set already
        txn = j.clients.tfchain.types.transactions.mint_definition_new()

        # add the minimum miner fee
        txn.miner_fee_add(self._minium_miner_fee)

        # set the new mint condition
        txn.mint_condition = j.clients.tfchain.types.conditions.from_recipient(minter)
        # minter definition must be of unlock type 1 or 3
        ut = txn.mint_condition.unlockhash.type
        if ut not in (UnlockHashType.PUBLIC_KEY, UnlockHashType.MULTI_SIG):
            raise ValueError("{} is an invalid unlock hash type and cannot be used for a minter definition".format(ut))

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
        return TransactionSendResult(txn, submit)

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

        The lock can be a str, or int:
            - when it is an int it represents either a block height or an epoch timestamp (in seconds)
            - when a str it can be a Jumpscale Datetime (e.g. '12:00:10', '31/10/2012 12:30', ...) or a Jumpscale Duration (e.g. '+ 2h', '+7d12h', ...)

        Returns a TransactionSendResult.

        @param recipient: see explanation above
        @param amount: int or str that defines the amount of TFT to set, see explanation above
        @param lock: optional lock that can be used to lock the sent amount to a specific time or block height, see explation above
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        """
        # create empty Mint Definition Txn, with a newly generated Nonce set already
        txn = j.clients.tfchain.types.transactions.mint_coin_creation_new()

        # add the minimum miner fee
        txn.miner_fee_add(self._minium_miner_fee)

        balance = self._wallet.balance

        # parse the output
        amount = Currency(value=amount)
        if amount <= 0:
            raise ValueError("no amount is defined to be sent")

        # define recipient
        recipient = j.clients.tfchain.types.conditions.from_recipient(recipient, lock=lock)
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
            addresses = self._wallet.addresses + balance.addresses_multisig
            for idx, co in enumerate(txn.coin_outputs):
                if str(co.condition.unlockhash) in addresses:
                    # add the id to the coin_output, so we can track it has been spent
                    co.id = txn.coin_outputid_new(idx)
                    balance.output_add(co, confirmed=False, spent=False)

        # return the txn, as well as the submit status as a boolean
        return TransactionSendResult(txn, submit)

    @property
    def _minium_miner_fee(self):
        """
        Returns the minimum miner fee
        """
        return self._wallet.client.minimum_miner_fee

    def _current_mint_condition_get(self):
        """
        Get the current mind condition from the parent TFChain client.
        """
        return self._wallet.client.minter.condition_get()

    def _transaction_put(self, transaction):
        """
        Submit the transaction to the network using the parent's wallet client.

        Returns the transaction ID.
        """
        return self._wallet.client.transaction_put(transaction=transaction)


from .types.ConditionTypes import ConditionAtomicSwap, OutputLock, AtomicSwapSecret, AtomicSwapSecretHash
from .types.FulfillmentTypes import FulfillmentAtomicSwap

class TFChainAtomicSwap():
    """
    TFChainAtomicSwap contains all Atomic Swap logic.
    """

    def __init__(self, wallet):
        if not isinstance(wallet, TFChainWallet):
            raise TypeError("wallet is expected to be a TFChainWallet")
        self._wallet = wallet

    def initiate(self, participator, amount, refund_time='+48h', source=None, refund=None, data=None, submit=True):
        """
        Initiate an atomic swap contract, targeted at the specified address,
        with the given amount. By default a 48 hours duration (starting from last block time)
        is used as time until contract can be refunded, but this can be changed.

        The participator is one of:
            - None: participator is the Free-For-All wallet
            - str (or unlockhash): participator is a personal wallet
            - list: participator is a MultiSig wallet where all owners (specified as a list of addresses) have to sign
            - tuple (addresses, sigcount): participator is a sigcount-of-addresscount MultiSig wallet

        The amount can be a str or an int:
            - when it is an int, you are defining the amount in the smallest unit (that is 1 == 0.000000001 TFT)
            - when defining as a str you can use the following space-stripped and case-insentive formats:
                - '123456789': same as when defining the amount as an int
                - '123.456': define the amount in TFT (that is '123.456' == 123.456 TFT == 123456000000)
                - '123456 TFT': define the amount in TFT (that is '123456 TFT' == 123456 TFT == 123456000000000)
                - '123.456 TFT': define the amount in TFT (that is '123.456 TFT' == 123.456 TFT == 123456000000)

        Returns the AtomicSwapInitiationResult.

        @param participator: see explanation above
        @param amount: int or str that defines the amount of TFT to set, see explanation above
        @param duration: the duration until the atomic swap contract becomes refundable
        @param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        @param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        @param submit: True by default, if False the transaction will not be sent even if possible (e.g. if you want to double check)
        """
        # create a random secret
        secret = AtomicSwapSecret.random()
        secret_hash = AtomicSwapSecretHash.from_secret(secret)

        # create the contract
        result = self._create_contract(
            recipient=participator, amount=amount, refund_time=refund_time,
            source=source, refund=refund, data=data, secret_hash=secret_hash,
            submit=submit)

        # return the contract, transaction, submission status as well as secret
        return AtomicSwapInitiationResult(
            AtomicSwapContract(coinoutput=result.transaction.coin_outputs[0], unspent=True,
                current_timestamp=self._chain_time),
            secret, result.transaction, result.submitted)
    
    def participate(self, initiator, amount, secret_hash, refund_time='+24h', source=None, refund=None, data=None, submit=True):
        """
        Initiate an atomic swap contract, targeted at the specified address,
        with the given amount. By default a 24 hours duration (starting from last block time)
        is used as time until contract can be refunded, but this can be changed.

        The amount can be a str or an int:
            - when it is an int, you are defining the amount in the smallest unit (that is 1 == 0.000000001 TFT)
            - when defining as a str you can use the following space-stripped and case-insentive formats:
                - '123456789': same as when defining the amount as an int
                - '123.456': define the amount in TFT (that is '123.456' == 123.456 TFT == 123456000000)
                - '123456 TFT': define the amount in TFT (that is '123456 TFT' == 123456 TFT == 123456000000000)
                - '123.456 TFT': define the amount in TFT (that is '123.456 TFT' == 123.456 TFT == 123456000000)

        Returns the AtomicSwapParticipationResult.

        @param initiator: str (or unlockhash) of a personal wallet
        @param amount: int or str that defines the amount of TFT to set, see explanation above
        @param secret_hash: the secret hash to be use, the same secret hash as used for the initiation contract
        @param duration: the duration until the atomic swap contract becomes refundable
        @param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        @param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (can only be a personal wallet address)
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        @param submit: True by default, if False the transaction will not be sent even if possible (e.g. if you want to double check)
        """
        # normalize secret hash
        secret_hash = AtomicSwapSecretHash(value=secret_hash)

        # create the contract and return the contract, transaction and submission status
        result = self._create_contract(
            recipient=initiator, amount=amount, refund_time=refund_time, source=source,
            refund=refund, data=data, secret_hash=secret_hash, submit=submit)
        return AtomicSwapParticipationResult(
            AtomicSwapContract(coinoutput=result.transaction.coin_outputs[0], unspent=True, current_timestamp=self._chain_time),
            result.transaction, result.submitted)
    
    def verify(self, outputid, amount=None, secret_hash=None, min_refund_time=None, sender=False, receiver=False, contract=None):
        """
        Verify the status and content of the Atomic Swap Contract linked to the given outputid.
        An exception is returned if the contract does not exist, has already been spent
        or is not valid according to this validation

        Returns the verified contract.

        @param outputid: str or Hash that identifies the coin output to whuich this contract is linked
        @param amount: validate amount if defined, int or str that defines the amount of TFT to set, see explanation above
        @param secret_hash: validate secret hash if defined, str or BinaryData
        @param min_refund_time: validate contract's refund time if defined, 0 if expected to be refundable, else the minimun time expected until it becomes refundable
        @param sender: if True it is expected that this wallet is registered as the sender of this contract
        @param receiver: if True it is expected that this wallet is registered as the receiver of this contract
        @param contract: if contract fetched in a previous call already, one can verify it also by directly passing it to this method
        """
        if contract is None:
            co = None
            spend_txn = None
            # try to fetch the contract
            try:
                # try to fetch the coin output that is expected to contain the secret
                co, _, spend_txn = self._wallet.client.coin_output_get(outputid)
            except j.clients.tfchain.errors.ExplorerNoContent as exc:
                raise j.clients.tfchain.errors.AtomicSwapContractNotFound(outputid=outputid) from exc
            # check if the contract hasn't been spent already
            if spend_txn is not None:
                # if a spend transaction exists,
                # it means the contract was already spend, and can therefore no longer be redeemed
                raise j.clients.tfchain.errors.AtomicSwapContractSpent(contract=AtomicSwapContract(
                    coinoutput=co, unspent=False, current_timestamp=self._chain_time), transaction=spend_txn)
            
            # create the unspent contract
            contract = AtomicSwapContract(coinoutput=co, unspent=True, current_timestamp=self._chain_time)
        elif not isinstance(contract, AtomicSwapContract):
            raise TypeError("contract was expected to be an AtomicSwapContract, not to be of type {}".format(type(contract)))
        else:
            # verify the outputid is the same
            if contract.outputid != outputid:
                raise j.clients.tfchain.errors.AtomicSwapContractInvalid(
                    message="output identifier is expected to be {}, not {}".format(str(outputid), str(contract.outputid)),
                    contract=contract)
        
        # if amount is given verify it
        if amount is not None:
            amount = Currency(value=amount)
            if amount != contract.amount:
                raise j.clients.tfchain.errors.AtomicSwapContractInvalid(
                    message="amount is expected to be {}, not {}".format(amount.str(with_unit=True), contract.amount.str(with_unit=True)),
                    contract=contract)
        
        # if secret hash is given verify it
        if secret_hash is not None:
            # normalize secret hash
            secret_hash = AtomicSwapSecretHash(value=secret_hash)
            if secret_hash != contract.secret_hash:
                raise j.clients.tfchain.errors.AtomicSwapContractInvalid(
                    message="secret_hash is expected to be {}, not {}".format(str(secret_hash), str(contract.secret_hash)),
                    contract=contract)
        
        # if min_refund_time is given verify it
        if min_refund_time is not None:
            chain_time = self._chain_time
            if isinstance(min_refund_time, str):
                min_refund_time = OutputLock(value=min_refund_time, current_timestamp=chain_time).value
            elif not isinstance(min_refund_time, int):
                raise TypeError("expected minimum refund time to be an integer or string, not to be of type {}".format(type(min_refund_time)))
            min_duration = max(0, min_refund_time-chain_time)
            chain_time = self._chain_time
            if chain_time >= contract.refund_timestamp:
                duration = 0
            else:
                duration = contract.refund_timestamp - chain_time
            if min_duration <= 0:
                if duration != 0:
                    raise j.clients.tfchain.errors.AtomicSwapContractInvalid(
                        message="contract cannot be refunded yet while it was expected to be possible already",
                        contract=contract)
            elif duration < min_duration:
                if duration == 0:
                    raise j.clients.tfchain.errors.AtomicSwapContractInvalid(
                        message="contract was expected to be non-refundable for at least {} more, but it can be refunded already since {}".format(
                            j.data.types.duration.toString(min_duration), j.data.time.epoch2HRDateTime(contract.refund_timestamp)),
                        contract=contract)
                elif duration < min_duration:
                    raise j.clients.tfchain.errors.AtomicSwapContractInvalid(
                        message="contract was expected to be available for redemption for at least {}, but it is only available for {}".format(
                            j.data.types.duration.toString(min_duration), j.data.types.duration.toString(duration)),
                        contract=contract)
        
        # if expected to be authorized to be the sender, verify this
        if sender and contract.sender not in self._wallet.addresses:
            raise j.clients.tfchain.errors.AtomicSwapContractInvalid(
                message="wallet not registered as sender of this contract", contract=contract)
        
        # if expected to be authorized to be the receiver, verify this
        if receiver and contract.receiver not in self._wallet.addresses:
            raise j.clients.tfchain.errors.AtomicSwapContractInvalid(
                message="wallet not registered as receiver of this contract", contract=contract)

        # return the contract for further optional consumption,
        # according to our validations it is valid
        return contract
    
    def redeem(self, outputid, secret, data=None):
        """
        Redeem an unspent Atomic Swap contract.

        Returns the sent transaction.

        @param outputid: the identifier of the coin output that contains the atomic swap contract
        @param secret: secret, matching the contract's secret hash, used to redeem the contract
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        """
        co = None
        spend_txn = None
        # try to fetch the contract
        try:
            # try to fetch the coin output that is expected to contain the secret
            co, _, spend_txn = self._wallet.client.coin_output_get(outputid)
        except j.clients.tfchain.errors.ExplorerNoContent as exc:
            raise j.clients.tfchain.errors.AtomicSwapContractNotFound(outputid=outputid) from exc
        # generate the contract
        contract = AtomicSwapContract(coinoutput=co, unspent=False, current_timestamp=self._chain_time) # either it is spent already or we'll spend it
        # check if the contract hasn't been spent already
        if spend_txn is not None:
            # if a spend transaction exists,
            # it means the contract was already spend, and can therefore no longer be redeemed
            raise j.clients.tfchain.errors.AtomicSwapContractSpent(contract=contract, transaction=spend_txn)
        # verify the defined secret
        if not contract.verify_secret(secret):
            raise j.clients.tfchain.errors.AtomicSwapInvalidSecret(contract=contract)
        
        # ensure this wallet is authorized to be the receiver
        if contract.receiver not in self._wallet.addresses:
            raise j.clients.tfchain.errors.AtomicSwapForbidden(message="unauthorized to redeem: wallet does not contain receiver address {}".format(contract.receiver), contract=contract)
        
        # create the fulfillment
        fulfillment = j.clients.tfchain.types.fulfillments.atomic_swap_new(secret=secret)

        # create, sign and submit the transaction
        return self._claim_contract(contract=contract, as_sender=False, fulfillment=fulfillment, data=data)
    
    def refund(self, outputid, data=None):
        """
        Refund an unspent Atomic Swap contract.

        Returns the sent transaction.

        @param outputid: the identifier of the coin output that contains the atomic swap contract
        @param data: optional data that can be attached ot the sent transaction (str or bytes), with a max length of 83
        """
        co = None
        spend_txn = None
        # try to fetch the contract
        try:
            # try to fetch the coin output that is expected to contain the secret
            co, _, spend_txn = self._wallet.client.coin_output_get(outputid)
        except j.clients.tfchain.errors.ExplorerNoContent as exc:
            raise j.clients.tfchain.errors.AtomicSwapContractNotFound(outputid=outputid) from exc
        # generate the contract
        contract = AtomicSwapContract(coinoutput=co, unspent=False, current_timestamp=self._chain_time) # either it is spent already or we'll spend it
        # check if the contract hasn't been spent already
        if spend_txn is not None:
            # if a spend transaction exists,
            # it means the contract was already spend, and can therefore no longer be redeemed
            raise j.clients.tfchain.errors.AtomicSwapContractSpent(contract=contract, transaction=spend_txn)
        # verify the contract can be refunded already
        time = self._chain_time
        if time < contract.refund_timestamp:
            raise j.clients.tfchain.errors.AtomicSwapForbidden(
                message="unauthorized to refund: contract can only be refunded since {}".format(j.data.time.epoch2HRDateTime(contract.refund_timestamp)),
                contract=contract)
        
        # ensure this wallet is authorized to be the sender (refunder)
        if contract.sender not in self._wallet.addresses:
            raise j.clients.tfchain.errors.AtomicSwapForbidden(message="unauthorized to refund: wallet does not contain sender address {}".format(contract.sender), contract=contract)
        
        # create the fulfillment
        fulfillment = j.clients.tfchain.types.fulfillments.atomic_swap_new()

        # create, sign and submit the transaction
        return self._claim_contract(contract=contract, as_sender=True, fulfillment=fulfillment, data=data)


    def _create_contract(self, recipient, amount, refund_time, source, refund, data, secret_hash, submit):
        """
        Create a new atomic swap contract,
        the logic for both the initiate as well as participate phase.
        """
        # define the amount
        amount = Currency(value=amount)
        if amount <= 0:
            raise ValueError("no amount is defined to be swapped")

        # define the miner fee
        miner_fee = self._minium_miner_fee

        # ensure the amount is bigger than the miner fee,
        # otherwise the contract cannot be redeemed/refunded
        if amount <= miner_fee:
            raise j.clients.tfchain.errors.AtomicSwapInsufficientAmountError(amount=amount, minimum_miner_fee=miner_fee)

        # define the coin inputs
        balance = self._wallet.balance
        inputs, remainder, suggested_refund = balance.fund(amount+miner_fee, source=source)

        # define the refund
        if refund is not None:
            refund = j.clients.tfchain.types.conditions.from_recipient(refund)
        elif suggested_refund is not None:
            refund = j.clients.tfchain.types.conditions.from_recipient(suggested_refund)
        else:
            refund = j.clients.tfchain.types.conditions.from_recipient(self._wallet.address)

        # define the sender
        if isinstance(refund, ConditionUnlockHash):
            sender = refund.unlockhash
        else:
            sender = self._wallet.address
        
        # create and populate the transaction
        txn = j.clients.tfchain.types.transactions.new()
        txn.coin_inputs = inputs
        txn.miner_fee_add(self._minium_miner_fee)
        txn.data = data

        # define refund time already, so we can use the chain time as the current time
        if isinstance(refund_time, str):
            chain_time = self._chain_time
            refund_time = OutputLock(value=refund_time, current_timestamp=chain_time).value
        elif not isinstance(refund_time, int):
            raise TypeError("expected refund time to be an integer or string, not to be of type {}".format(type(refund_time)))

        # define the atomic swap contract and add it as a coin output
        asc = j.clients.tfchain.types.conditions.atomic_swap_new(
            sender=sender, receiver=recipient, hashed_secret=secret_hash, lock_time=refund_time)
        txn.coin_output_add(condition=asc, value=amount)

        # optionally add a refund coin output
        if remainder > 0:
            txn.coin_output_add(condition=refund, value=remainder)

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

        # assign all coin output ID's for atomic swap contracts,
        # as we always care about the contract's output ID and
        # the refund coin output has to be our coin output
        for idx, co in enumerate(txn.coin_outputs):
            co.id = txn.coin_outputid_new(idx)

        # submit if possible
        submit = submit and txn.is_fulfilled()
        if submit:
            txn.id = self._transaction_put(transaction=txn)
            # update balance
            for ci in txn.coin_inputs:
                balance.output_add(ci.parent_output, confirmed=False, spent=True)
            addresses = self._wallet.addresses + balance.addresses_multisig
            for idx, co in enumerate(txn.coin_outputs):
                if str(co.condition.unlockhash) in addresses:
                    balance.output_add(co, confirmed=False, spent=False)

        # return the txn, as well as the submit status as a boolean
        return TransactionSendResult(txn, submit)
        
    def _claim_contract(self, contract, as_sender, fulfillment, data):
        """
        claim an unspent atomic swap contract
        """
        # create the contract and fill in the easy content
        txn = j.clients.tfchain.types.transactions.new()
        miner_fee = self._minium_miner_fee
        txn.miner_fee_add(miner_fee)
        txn.data = data
        # define the coin input
        txn.coin_input_add(parentid=contract.outputid, fulfillment=fulfillment, parent_output=contract.coin_output)
        # and the coin output
        txn.coin_output_add(
            condition=j.clients.tfchain.types.conditions.unlockhash_new(contract.sender if as_sender else contract.receiver),
            value=contract.amount-miner_fee)
        
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

        # submit if possible
        submit = txn.is_fulfilled()
        if not submit:
            raise Exception("BUG: transaction should be fulfilled at ths point, please fix or report as an isuse")
        
        # assign transactionid
        txn.id = self._transaction_put(transaction=txn)
        # update balance
        balance = self._wallet.balance
        addresses = self._wallet.addresses
        for idx, co in enumerate(txn.coin_outputs):
            if str(co.condition.unlockhash) in addresses:
                co.id = txn.coin_outputid_new(idx)
                balance.output_add(co, confirmed=False, spent=False)

        # return the txn
        return txn

    @property
    def _chain_time(self):
        """
        Returns the time according to the chain's network.
        """
        info = self._wallet.client.blockchain_info_get()
        return info.timestamp

    @property
    def _minium_miner_fee(self):
        """
        Returns the minimum miner fee
        """
        return self._wallet.client.minimum_miner_fee

    def _output_get(self, outputid):
        """
        Get the transactions linked to the given outputID.

        @param: id of te
        """
        return self._wallet.client.output_get(outputid)

    def _transaction_put(self, transaction):
        """
        Submit the transaction to the network using the parent's wallet client.

        Returns the transaction ID.
        """
        return self._wallet.client.transaction_put(transaction=transaction)


class TFChainThreeBot():
    """
    TFChainThreeBot contains all ThreeBot logic.
    """
    
    def __init__(self, wallet):
        if not isinstance(wallet, TFChainWallet):
            raise TypeError("wallet is expected to be a TFChainWallet")
        self._wallet = wallet

    def record_new(self, months=1, names=None, addresses=None, key_index=None, source=None, refund=None):
        """
        Create a new 3Bot by creating a new record on the BlockChain,
        by default 1 month rent is already paid for the 3Bot, but up to 24 months can immediately be pre-paid
        against a discount if desired.

        At least one name or one address is required, and up to 5 names and 10 addresses can
        exists for a single 3Bot.

        If no key_index is given a new key pair is generated for the wallet,
        otherwise the key pair on the given index of the wallet is used.

        Returns a TransactionSendResult.

        @param months: amount of months to be prepaid, at least 1 month is required, maximum 24 months is allowed
        @param names: 3Bot Names to add to the 3Bot as aliases (minumum 0, maximum 5)
        @param addresses: Network Addresses used to reach the 3Bot (minimum 0, maximum 10)
        @param key_index: if None is given a new key pair is generated, otherwise the key pair on the defined index is used.
        @param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        @param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        """
        # create the txn and fill the easiest properties already
        txn = j.clients.tfchain.types.transactions.threebot_registration_new()
        txn.number_of_months = months
        if names is None and addresses is None:
            raise ValueError("at least one name or one address is to be given, none is defined")
        txn.names = names
        txn.addresses = addresses

        # get the fees, and fund the transaction
        balance = self._fund_txn(txn, source, refund)

        # if the key_index is not defined, generate a new public key,
        # otherwise use the key_index given
        if key_index is None:
            txn.public_key = self._wallet.public_key_new()
        else:
            if not isinstance(key_index, int):
                raise TypeError("key index is to be of type int, not type {}".format(type(key_index)))
            addresses = self._wallet.addresses
            if key_index < 0 or key_index >= len(addresses):
                raise ValueError("key index {} is OOB, index cannot be negative, and can be maximum {}".format(key_index, len(addresses)-1))
            txn.public_key = self._wallet.key_pair_get(unlockhash=addresses[key_index]).public_key

        # sign, submit, update Balance and return result
        return self._sign_and_submit_txn(txn, balance)

    def record_update(self, identifier, months=0, names_to_add=None, names_to_remove=None, addresses_to_add=None, addresses_to_remove=None, source=None, refund=None):
        """
        Update the record of an existing 3Bot, for which this Wallet is authorized to make such changes.
        Names and addresses can be added and removed. Removal of data is always for free, adding data costs money.
        Extra months can also be paid (up to 24 months in total), as to extend the expiration time further in the future.

        One of months, names_to_add, names_to_remove, addresses_to_add, addresses_to_remove has to be a value other than 0/None.

        Returns a TransactionSendResult.

        @param months: amount of months to be paid and added to the current months, if the 3Bot was inactive, the starting time will be now
        @param names_to_add: 3Bot Names to add to the 3Bot as aliases (minumum 0, maximum 5)
        @param names_to_remove: 3Bot Names to add to the 3Bot as aliases (minumum 0, maximum 5)
        @param addresses_to_add: Network Addresses to add and used to reach the 3Bot (minimum 0, maximum 10)
        @param addresses_to_remove: Network Addresses to remove and used to reach the 3Bot (minimum 0, maximum 10)
        @param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        @param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        """
        if months < 1 and not reduce((lambda r, v: r or (v is not None)), [names_to_add, names_to_remove, addresses_to_add, addresses_to_remove], False):
            raise ValueError("extra months is to be given or one name/address is to be added/removed, none is defined")
    
        # create the txn and fill the easiest properties already
        txn = j.clients.tfchain.types.transactions.threebot_record_update_new()
        txn.botid = identifier
        txn.number_of_months = months
        txn.names_to_add = names_to_add
        txn.names_to_remove = names_to_remove
        txn.addresses_to_add = addresses_to_add
        txn.addresses_to_remove = addresses_to_remove

        # get the 3Bot Public Key
        record = self._wallet.client.threebot.record_get(identifier)
        # set the parent public key
        txn.parent_public_key = record.public_key

        # ensure the 3Bot is either active, or will be come active
        if record.expiration <= self._chain_time and months == 0:
            raise j.clients.tfchain.errors.ThreeBotInactive(identifier, record.expiration)

        # get the fees, and fund the transaction
        balance = self._fund_txn(txn, source, refund)

        # sign, submit, update Balance and return result
        return self._sign_and_submit_txn(txn, balance)

    def name_transfer(self, sender, receiver, names, source=None, refund=None):
        """
        Transfer one or multiple 3Bot names from the sender 3Bot to the receiver 3Bot.
        Both the Sender and Receiver 3Bots have to be active at the time of transfer.

        Returns a TransactionSendResult.

        @param sender: identifier of the existing and active 3Bot sender bot
        @param receiver: identifier of the existing and active 3Bot receiver bot
        @param names: 3Bot Names to transfer (minumum 0, maximum 5)
        @param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        @param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        """
        # create the txn and fill the easiest properties already
        txn = j.clients.tfchain.types.transactions.threebot_name_transfer_new()
        txn.sender_botid = sender
        txn.receiver_botid = receiver
        txn.names = names
        if len(txn.names) == 0:
            raise ValueError("at least one (3Bot) name has to be transfered, but none were defined")

        # keep track of chain time
        chain_time = self._chain_time

        # get and assign the 3Bot's public key for the sender
        record = self._wallet.client.threebot.record_get(sender)
        txn.sender_parent_public_key = record.public_key
        # ensure sender bot is active
        if record.expiration <= chain_time:
            raise j.clients.tfchain.errors.ThreeBotInactive(sender, record.expiration)

        # get and assign the 3Bot's public key for the receiver
        record = self._wallet.client.threebot.record_get(receiver)
        txn.receiver_parent_public_key = record.public_key
        # ensure receiver bot is active
        if record.expiration <= chain_time:
            raise j.clients.tfchain.errors.ThreeBotInactive(receiver, record.expiration)

        # get the fees, and fund the transaction
        balance = self._fund_txn(txn, source, refund)

        # sign and update Balance and return result,
        # only if the 3Bot owns both public keys, the Txn will be already,
        # submitted as well
        return self._sign_and_submit_txn(txn, balance)


    def _fund_txn(self, txn, source, refund):
        """
        common fund/refund/inputs/fees logic for all 3Bot Transactions
        """
        # get the fees, and fund the transaction
        miner_fee = self._minium_miner_fee
        bot_fee = txn.required_bot_fees
        balance = self._wallet.balance
        inputs, remainder, suggested_refund = balance.fund(miner_fee+bot_fee, source=source)

        # add the coin inputs
        txn.coin_inputs = inputs

        # add refund coin output if needed
        if remainder > 0:
            # define the refund condition
            if refund is None: # automatically choose a refund condition if none is given
                if suggested_refund is None:
                    refund = j.clients.tfchain.types.conditions.unlockhash_new(unlockhash=self._wallet.address)
                else:
                    refund = suggested_refund
            else:
                # use the given refund condition (defined as a recipient)
                refund = j.clients.tfchain.types.conditions.from_recipient(refund)
            txn.refund_coin_output_set(value=remainder, condition=refund)
        # add the miner fee
        txn.transaction_fee = miner_fee

        # return balance object
        return balance
    
    def _sign_and_submit_txn(self, txn, balance):
        """
        common sign and submit logic for all 3Bot Transactions
        """
        # generate the signature requests
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

        # txn should be fulfilled now
        submit = txn.is_fulfilled()
        if submit:
            # submit the transaction
            txn.id = self._transaction_put(transaction=txn)

            # update balance
            for ci in txn.coin_inputs:
                balance.output_add(ci.parent_output, confirmed=False, spent=True)
            addresses = self._wallet.addresses + balance.addresses_multisig
            for idx, co in enumerate(txn.coin_outputs):
                if str(co.condition.unlockhash) in addresses:
                    # add the id to the coin_output, so we can track it has been spent
                    co.id = txn.coin_outputid_new(idx)
                    balance.output_add(co, confirmed=False, spent=False)
        # and return the created/submitted transaction for optional user consumption
        return TransactionSendResult(txn, submit)

    @property
    def _minium_miner_fee(self):
        """
        Returns the minimum miner fee
        """
        return self._wallet.client.minimum_miner_fee

    def _transaction_put(self, transaction):
        """
        Submit the transaction to the network using the parent's wallet client.

        Returns the transaction ID.
        """
        return self._wallet.client.transaction_put(transaction=transaction)

    @property
    def _chain_time(self):
        """
        Returns the time according to the chain's network.
        """
        info = self._wallet.client.blockchain_info_get()
        return info.timestamp


class TFChainERC20():
    """
    TFChainERC20 contains all ERC20 (wallet) logic.
    """
    
    def __init__(self, wallet):
        if not isinstance(wallet, TFChainWallet):
            raise TypeError("wallet is expected to be a TFChainWallet")
        self._wallet = wallet

    def coins_send(self, address, amount, source=None, refund=None):
        """
        Send the specified amount of coins to the given ERC20 address.

        The amount can be a str or an int:
            - when it is an int, you are defining the amount in the smallest unit (that is 1 == 0.000000001 TFT)
            - when defining as a str you can use the following space-stripped and case-insentive formats:
                - '123456789': same as when defining the amount as an int
                - '123.456': define the amount in TFT (that is '123.456' == 123.456 TFT == 123456000000)
                - '123456 TFT': define the amount in TFT (that is '123456 TFT' == 123456 TFT == 123456000000000)
                - '123.456 TFT': define the amount in TFT (that is '123.456 TFT' == 123.456 TFT == 123456000000)

        Returns a TransactionSendResult.
        
        @param address: str or ERC20Address value to which the money is to be send
        @param amount: int or str that defines the amount of TFT to set, see explanation above
        @param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        @param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        """
        amount = Currency(value=amount)
        if amount <= 0:
            raise ValueError("no amount is defined to be sent")

        # create transaction
        txn = j.clients.tfchain.types.transactions.erc20_convert_new()
        # define the amount and recipient
        txn.address = ERC20Address(value=address)
        txn.value = amount

        # fund the transaction
        balance = self._fund_txn(txn, source, refund, txn.value)

        # sign, submit and return the transaction
        return self._sign_and_submit_txn(txn, balance)

    def address_register(self, value=None, source=None, refund=None):
        """
        Register an existing TFT address of this wallet as an ERC20 Withdraw Address,
        either by specifying the address itself or by specifying the index of the address.
        If no value is defined a new key pair will be defined.

        Returns a TransactionSendResult.
        
        @param value: index of the TFT address or address itself, the address has to be owned by this wallet
        @param source: one or multiple addresses/unlockhashes from which to fund this coin send transaction, by default all personal wallet addresses are used, only known addresses can be used
        @param refund: optional refund address, by default is uses the source if it specifies a single address otherwise it uses the default wallet address (recipient type, with None being the exception in its interpretation)
        """
        if value is None:
            public_key = self._wallet.public_key_new()
        elif isinstance(value, (str, UnlockHash)):
            try:
                public_key = self._wallet.key_pair_get(unlockhash=value).public_key
            except KeyError as exc:
                if isinstance(value, str):
                    value = UnlockHash.from_json(value)
                raise j.clients.tfchain.errors.ERC20RegistrationForbidden(address=value) from exc
        elif isinstance(value, int) and not isinstance(value, bool):
            addresses = self._wallet.addresses
            if value < 0 or value >= len(addresses):
                raise ValueError("address index {} is not a valid index for this wallet, has to be in the inclusive range of [0, {}]".format(
                    value, len(addresses)-1))
            public_key = self._wallet.key_pair_get(unlockhash=addresses[value]).public_key
        else:
            raise ValueError("value has to be a str, UnlockHash or int, cannot identify an address using value {} (type: {})".format(value, type(value)))

        # create transaction
        txn = j.clients.tfchain.types.transactions.erc20_address_registration_new()
        # define the public key
        txn.public_key = public_key

        # fund the transaction
        balance = self._fund_txn(txn, source, refund, txn.registration_fee)

        # sign, submit and return the transaction
        return self._sign_and_submit_txn(txn, balance)

    def address_get(self, value=None):
        """
        Get the registration info of an existing TFT address of this wallet as an ERC20 Withdraw Address,
        either by specifying the address itself or by specifying the index of the address.
        If no value is defined the first wallet address will be used.

        Returns an ERC20AddressInfo named tuple.
        
        @param value: index of the TFT address or address itself, the address has to be owned by this wallet
        """
        if value is None:
            public_key = self._wallet.key_pair_get(unlockhash=self._wallet.address).public_key
        elif isinstance(value, (str, UnlockHash)):
            try:
                public_key = self._wallet.key_pair_get(unlockhash=value).public_key
            except KeyError as exc:
                if isinstance(value, str):
                    value = UnlockHash.from_json(value)
                raise j.clients.tfchain.errors.AddressNotInWallet(address=value) from exc
        elif isinstance(value, int) and not isinstance(value, bool):
            addresses = self._wallet.addresses
            if value < 0 or value >= len(addresses):
                raise ValueError("address index {} is not a valid index for this wallet, has to be in the inclusive range of [0, {}]".format(
                    value, len(addresses)-1))
            public_key = self._wallet.key_pair_get(unlockhash=addresses[value]).public_key
        else:
            raise ValueError("value has to be a str, UnlockHash or int, cannot identify an address using value {} (type: {})".format(value, type(value)))

        # look up the wallet address and return it
        return self._wallet.client.erc20.address_get(unlockhash=public_key.unlockhash)

    def addresses_get(self):
        """
        Get the information for all registered ERC20 withdraw addresses.
        Can return a empty list if no addresses of this wallet were registered as an ERC20 withdraw address.

        Returns a list of ERC20AddressInfo named tuples.
        """
        results = []
        # scan for some new keys first, to ensure we get all addresses
        self._wallet._key_scan()
        # get the ERC20 info for all addresses that are registered as ERC20 withdraw addresses, if any
        for address in self._wallet.addresses:
            try:
                info = self._wallet.client.erc20.address_get(address)
                results.append(info)
            except j.clients.tfchain.errors.ExplorerNoContent:
                pass
        # return all found info, if anything
        return results

    def _fund_txn(self, txn, source, refund, amount):
        """
        common fund/refund/inputs/fees logic for all ERC20 Transactions
        """
        # get the fees, and fund the transaction
        miner_fee = self._minium_miner_fee
        balance = self._wallet.balance
        inputs, remainder, suggested_refund = balance.fund(miner_fee+amount, source=source)

        # add the coin inputs
        txn.coin_inputs = inputs

        # add refund coin output if needed
        if remainder > 0:
            # define the refund condition
            if refund is None: # automatically choose a refund condition if none is given
                if suggested_refund is None:
                    refund = j.clients.tfchain.types.conditions.unlockhash_new(unlockhash=self._wallet.address)
                else:
                    refund = suggested_refund
            else:
                # use the given refund condition (defined as a recipient)
                refund = j.clients.tfchain.types.conditions.from_recipient(refund)
            txn.refund_coin_output_set(value=remainder, condition=refund)

        # add the miner fee
        txn.transaction_fee = miner_fee

        # return balance object
        return balance
    
    def _sign_and_submit_txn(self, txn, balance):
        """
        common sign and submit logic for all ERC20 Transactions
        """
        # generate the signature requests
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

        # txn should be fulfilled now
        submit = txn.is_fulfilled()
        if submit:
            # submit the transaction
            txn.id = self._transaction_put(transaction=txn)

            # update balance
            for ci in txn.coin_inputs:
                balance.output_add(ci.parent_output, confirmed=False, spent=True)
            addresses = self._wallet.addresses + balance.addresses_multisig
            for idx, co in enumerate(txn.coin_outputs):
                if str(co.condition.unlockhash) in addresses:
                    # add the id to the coin_output, so we can track it has been spent
                    co.id = txn.coin_outputid_new(idx)
                    balance.output_add(co, confirmed=False, spent=False)

        # and return the created/submitted transaction for optional user consumption
        return TransactionSendResult(txn, submit)

    @property
    def _minium_miner_fee(self):
        """
        Returns the minimum miner fee
        """
        return self._wallet.client.minimum_miner_fee

    def _transaction_put(self, transaction):
        """
        Submit the transaction to the network using the parent's wallet client.

        Returns the transaction ID.
        """
        return self._wallet.client.transaction_put(transaction=transaction)


from typing import NamedTuple

class TransactionSendResult(NamedTuple):
    """
    TransactionSendResult is a named tuple,
    used as the result for a generic transaction send call.
    """
    transaction: TransactionBaseClass
    submitted: bool

class TransactionSignResult(NamedTuple):
    """
    TransactionSignResult is a named tuple,
    used as the result for a transaction sign call.
    """
    transaction: TransactionBaseClass
    signed: bool
    submitted: bool

class AtomicSwapInitiationResult(NamedTuple):
    """
    AtomicSwapInitiationResult is a named tuple,
    used as the result for an atomic swap initiation call.
    """
    contract: AtomicSwapContract
    secret: AtomicSwapSecret
    transaction: TransactionBaseClass
    submitted: bool

class AtomicSwapParticipationResult(NamedTuple):
    """
    AtomicSwapParticipationResult is a named tuple,
    used as the result for an atomic swap participation call.
    """
    contract: AtomicSwapContract
    transaction: TransactionBaseClass
    submitted: bool

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
        return self._public_key.unlockhash

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
        # all wallet addresses tracked in this wallet
        self._addresses = set()

    @property
    def addresses(self):
        """
        All (personal wallet) addresses for which an output is tracked in this Balance.
        """
        return list(self._addresses)

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
        self._addresses.add(str(output.condition.unlockhash))
    
    @property
    def _base(self):
        """
        Private helper utility to return this class as a new and pure WalletBalance object
        """
        b = WalletBalance()
        b._outputs = self._outputs
        b._outputs_spent = self._outputs_spent
        b._outputs_unconfirmed = self._outputs_unconfirmed
        b._outputs_unconfirmed_spent = self._outputs_unconfirmed_spent
        b._chain_blockid = self._chain_blockid
        b._chain_height = self._chain_height
        b._chain_time = self._chain_time
        b._addresses = self._addresses
        return b

    def balance_add(self, other):
        """
        Merge the content of the other balance into this balance.
        If other is None, this call results in a no-op.

        Always assign the result, as it could other than self,
        should the class type be changed in order to add all content correctly.
        """
        if other is None:
            return self
        if isinstance(other, (WalletsBalance, MultiSigWalletBalance)):
            return WalletsBalance().balance_add(self).balance_add(other)
        if not isinstance(other, WalletBalance):
            raise TypeError("other balance has to be of type wallet balance")
        # another balance is defined, create a new balance that will contain our merge
        # merge the chain info
        if self.chain_height >= other.chain_height:
            if self.chain_time < other.chain_time:
                raise ValueError("chain time and chain height of balances do not match")
        else:
            if self.chain_time >= other.chain_time:
                raise ValueError("chain time and chain height of balances do not match")
            self.chain_time = other.chain_time
            self.chain_height = other.chain_height
            self.chain_blockid = other.chain_blockid
        # merge the outputs
        for attr in ['_outputs', '_outputs_spent', '_outputs_unconfirmed', '_outputs_unconfirmed_spent']:
            d = getattr(self, attr, {})
            for id, output in getattr(other, attr, {}).items():
                d[id] = output
        # merge the addresses
        self._addresses |= other._addresses
        # return the modified self
        return self

    def drain(self, recipient, miner_fee, unconfirmed=False, data=None, lock=None):
        """
        add all available outputs into as many transactions as required,
        by default only confirmed outputs are used, if unconfirmed=True
        it will use unconfirmed available outputs as well.

        Result can be an empty list if no outputs were available.

        @param recipient: required recipient towards who the drained coins will be sent
        @param the miner fee to be added to all sent transactions
        @param unconfirmed: optionally drain unconfirmed (available) outputs as well
        @param data: optional data that can be attached ot the created transactions (str or bytes), with a max length of 83
        @param lock: optional lock that can be attached to the sent coin outputs
        """
        # define recipient
        recipient = j.clients.tfchain.types.conditions.from_recipient(recipient, lock=lock)

        # validate miner fee
        if not isinstance(miner_fee, Currency):
            raise TypeError("miner fee has to be a currency")
        if miner_fee == 0:
            raise ValueError("a non-zero miner fee has to be defined")

        # collect all transactions in one list
        transactions = []

        # collect all confirmed (available) outputs
        outputs = self.outputs_available
        if unconfirmed:
            # if also the unconfirmed_avaialble) outputs are desired, let's add them as well
            outputs += self.outputs_unconfirmed_available
        # drain all outputs
        while len(outputs) > 0:
            txn = j.clients.tfchain.types.transactions.new()
            txn.data = data
            txn.miner_fee_add(miner_fee)
            # select maximum _MAX_RIVINE_TRANSACTION_INPUTS outputs
            n = min(len(outputs), _MAX_RIVINE_TRANSACTION_INPUTS)
            used_outputs = outputs[:n]
            outputs = outputs[n:] # and update our output list, so we do not double spend
            # compute amount, minus minimum fee and add our only output
            amount = sum([co.value for co in used_outputs]) - miner_fee
            txn.coin_output_add(condition=recipient, value=amount)
            # add the coin inputs
            txn.coin_inputs = [CoinInput.from_coin_output(co) for co in used_outputs]
            # append the transaction
            transactions.append(txn)

        # return all created transactions, if any
        return transactions

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

    def balance_add(self, other):
        """
        Merge the content of the other balance into this balance.
        If other is None, this call results in a no-op.

        Always assign the result, as it could other than self,
        should the class type be changed in order to add all content correctly.
        """
        if other is None:
            return self
        if not isinstance(other, MultiSigWalletBalance):
            if isinstance(other, (WalletBalance, WalletsBalance)):
                return WalletsBalance().balance_add(self).balance_add(self)
            # can only merge 2 multi-signature wallet balances
            raise TypeError("other balance has to be of type multi-signature wallet balance")
        if self.address != other.addres:
            raise ValueError("other balance is for a different MultiSignature Wallet, cannot be merged")
        # piggy-back on the super class for the actual merge logic
        return super().balance_add(other._base)

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

    @property
    def addresses_multisig(self):
        """
        All (multisig wallet) addresses for which an output is tracked in this Balance.
        For each address you'll find a wallet in the `self.wallets` dict property.
        """
        return list(self.wallets.keys())

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
        self._addresses.add(str(uh))
        return super().output_add(output=output, confirmed=confirmed, spent=spent)

    def balance_add(self, other):
        """
        Merge the content of the other balance into this balance.
        If other is None, this call results in a no-op.

        Always assign the result, as it could other than self,
        should the class type be changed in order to add all content correctly.
        """
        if other is None:
            return self
        if not isinstance(other, WalletBalance):
            raise TypeError("other balance has to be of type wallet balance")
        if isinstance(other, MultiSigWalletBalance):
            self._merge_multisig_wallet_balance(other.address, other)
            return self
        # piggy-back on the super class for the actual output merge logic
        b = super().balance_add(other._base)
        if b != self:
            raise Exception("BUG: instance shouldn't have changed, please fix or report")
        if not isinstance(other, WalletsBalance):
            return b # return as nothing else can be merged
        # merge all the multi-signature wallets
        for addr, balance in other._wallets.items():
            b._merge_multisig_wallet_balance(addr, balance)
        # return the merged balance
        return b
    
    def _merge_multisig_wallet_balance(self, address, balance):
        """
        Assign or merge a multi-sig wallet balance
        """
        if address not in self._wallets:
            self._wallets[address] = balance
            return
        self._wallets[address] = self._wallets[address].merge(balance)

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
            raise j.clients.tfchain.errors.InsufficientFunds("no addresses defined or linked to this wallet")

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
            raise j.clients.tfchain.errors.InsufficientFunds("not enough funds available in the individual wallet to fund the requested amount")
        # otherwise keep going for multisig addresses
        outputs, collected = self._fund_multisig(amount, ms_addresses, outputs=outputs, collected=collected)

        # if we still didn't manage to fund enough, there is nothing we can do
        if collected < amount:
            raise j.clients.tfchain.errors.InsufficientFunds("not enough funds available in the wallets to fund the requested amount")
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
            if len(outputs) > _MAX_RIVINE_TRANSACTION_INPUTS:
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
            if len(outputs) > _MAX_RIVINE_TRANSACTION_INPUTS:
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
                if len(outputs) > _MAX_RIVINE_TRANSACTION_INPUTS:
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
                if len(outputs) > _MAX_RIVINE_TRANSACTION_INPUTS:
                    # to not reach the input limit
                    collected -= outputs.pop(0).value
                if collected >= amount:
                    return outputs, collected
        # we return whatever we have collected, no matter if it is sufficient
        return outputs, collected
