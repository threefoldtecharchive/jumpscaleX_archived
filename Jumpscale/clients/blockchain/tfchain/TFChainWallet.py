
from Jumpscale import j

from ed25519 import SigningKey

from .types.PrimitiveTypes import Currency
from .types.CryptoTypes import PublicKey, UnlockHash
from .types.errors import ExplorerNoContent
from .types.errors import InsufficientFunds
from .types.CompositionTypes import CoinOutput, CoinInput
from .types.ConditionTypes import ConditionNil, ConditionUnlockHash, ConditionLockTime

class TFChainWallet(j.application.JSBaseConfigClass):
    """
    Tfchain Wallet object
    """
    _SCHEMATEXT = """
        @url = jumpscale.tfchain.wallet
        name* = "" (S)
        seed = "" (S)
        key_count = 1 (I)

        key_scan_count = 3 (I)
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
 
    def _data_trigger_new(self):
        # provide sane defaults for the schema-based wallet config
        if self.seed == "":
            self.seed = j.data.encryption.mnemonic.generate(strength=256)
        if self.key_count < 1:
            self.key_count = 1
        if self.key_scan_count < 0:
            self.key_scan_count = 0

        # generate keys
        keys_to_generate = self.key_count
        self.key_count = 0
        # generate the primary address
        self._primary_address = str(self._key_pair_new().unlock_hash())
        # generate the other addresses
        for _ in range(keys_to_generate-1):
            self._key_pair_new()

    @property
    def network_type(self):
        """
        The network type, defined by the parent TFChain client,
        that this wallet is operating on.

        Changing the network type has to be done from the parent TFChain client.
        """
        return self._parent._parent.network_type

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
    def balance(self):
        """
        The balance "sheet" of the wallet.
        """
        # first get chain info, so we can check if the current balance is still fine
        info = self._parent._parent.blockchain_info_get()
        if self._cached_balance and self._cached_balance.chain_height == info.height:
            return self._cached_balance

        # TODO: support extra address key scanning, this call is the perfect opportunity to try that
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
        # cache the balance
        self._cached_balance = balance
        # return the balance
        return balance

    def coins_send(self, recipient, amount, lock=None, data=None):
        """
        Send the specified amount of coins to the given recipient,
        optionally locked. Arbitrary data can be attached as well if desired.

        The recipient is one of:
            - None: recipient is the Free-For-All wallet
            - str (or unlockhash): recipient is a personal wallet
            - list: recipient is a MultiSig wallet where all owners (specified as a list of addresses) have to sign
            - tuple (addresses, sigcount): recipient is a sigcount-of-addresscount MultiSig wallet
        
        @param recipient: see explanation above
        @param amount: int that defines the amount of coins to be sent note that 1 TFT == 1000000000
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
        minerfee = self._miner_fee_get()
        outputs, remainder = balance.fund(amount+minerfee)

        # create transaction
        txn = j.clients.tfchain.transactions.new()
        # add main coin output
        txn.coin_output_add(value=amount, condition=recipient)
        # add refund coin output if needed
        if remainder > 0:
            txn.coin_output_add(value=remainder, condition=j.clients.tfchain.types.conditions.unlockhash_new(unlockhash=self.address))
        # add the miner fee
        txn.miner_fee_add(minerfee)

        # add the coin inputs
        txn.coin_inputs = self.coin_inputs_from(outputs)
        
        # if there is data to be added, add it as well
        if data:
            txn.data = data

        # sign all inputs of the transaction
        for idx, ci in enumerate(txn.coin_inputs):
            address = str(ci.parent_output.condition.unlockhash)
            keypair = self.key_pair_get(address)
            signhash = txn.signature_hash_get(idx)
            ci.fulfillment.signature, _ = keypair.sign(signhash)

        # submit the transaction
        txn.id = self._transaction_put(transaction=txn)

        # update balance
        for ci in txn.coin_inputs:
            balance.output_add(ci.parent_output, confirmed=False, spent=True)
        addresses = self.addresses
        for co in txn.coin_outputs:
            if str(co.condition.unlockhash) in addresses:
                balance.output_add(co, confirmed=False, spent=False)
        # and return the created/submitted transaction for optional user consumption
        return txn

    def address_new(self):
        """
        Generate a new wallet address,
        using the wallet's seed and the current key index as input.

        An address, also known as unlock hash,
        is a blake2 hash of the public key that is linked to a private key.
        The public key is used for verification of signatures,
        that were created with the matching private key.
        """
        return str(self._key_pair_new().unlock_hash())
    
    def coin_inputs_from(self, outputs):
        """
        Transform the given coin outputs, owned by this wallet,
        into coin inputs.
        """
        inputs = []
        for co in outputs:
            assert isinstance(co, CoinOutput)
            fulfillment = self.fulfillment_from(co.condition)
            ci = CoinInput(parent_id=co.id, fulfillment=fulfillment)
            ci.parent_output = co
            inputs.append(ci)
        return inputs

    def fulfillment_from(self, condition):
        """
        Get a matching fulfillment from a given condition,
        only possible if the condition is "owned" by this wallet.
        """
        if isinstance(condition, ConditionLockTime):
            condition = condition.condition
        if isinstance(condition, ConditionNil):
            pair = self.key_pair_get(self.address)
            return j.clients.tfchain.types.fulfillments.single_signature_new(pub_key=pair.public_key)
        elif isinstance(condition, ConditionUnlockHash):
            pair = self.key_pair_get(str(condition.unlockhash))
            return j.clients.tfchain.types.fulfillments.single_signature_new(pub_key=pair.public_key)
        else:
            raise TypeError("given condition is invalid: {}", type(condition))

    def public_key_new(self):
        """
        Generate a new wallet public key,
        using the wallet's seed and the current key index as input.
        """
        return self._key_pair_new().public_key

    def key_pair_get(self, unlock_hash):
        """
        Get the private/public key pair for the given unlock hash.
        If the unlock has is not owned by this wallet a KeyError exception is raised.
        """
        if isinstance(unlock_hash, UnlockHash):
            unlock_hash = str(unlock_hash)
        else:
            assert type(unlock_hash) is str
        key = self._key_pairs.get(unlock_hash)
        if key is None:
            raise KeyError("wallet does not own unlock hash {}".format(unlock_hash))
        return key

    def _unlockhash_get(self, address):
        return self._parent._parent.unlockhash_get(address)

    def _transaction_put(self, transaction):
        return self._parent._parent.transaction_put(transaction)
        
    def _miner_fee_get(self):
        """
        The (minimum) miner fee as defined by the TFChain client.
        """
        return self._parent._parent.minimum_minerfee

    def _key_pair_new(self, integrate=True):
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
        e.add(self.key_count)
        seed_hash = bytes.fromhex(j.data.hash.blake2_string(e.data))
        private_key = SigningKey(seed_hash)
        public_key = private_key.get_verifying_key()
        
        key_pair = SpendableKey(
            public_key = j.clients.tfchain.types.public_key_new(hash=public_key.to_bytes()),
            private_key = private_key)

        # if we wish to integrate (mostly when we're not scanning),
        # we also add it to our wallets known key pairs
        if integrate:
            self._key_pair_add(key_pair)

        return key_pair

    def _key_pair_add(self, key_pair, add_count=True):
        """
        A private utility function that is used by default
        by the _key_pair_new wallet method to integrate a newly created key pair
        into this wallet's key pair dictionary.

        This method is seperate as we also scan for other keys during the fetching
        of the balance of a wallet. When we do, we want to create new key pairs,
        but only integrate them, if indeed we found the key (or a key after it) was used.
        """
        addr = str(key_pair.unlock_hash())
        assert addr not in self._key_pairs
        self._key_pairs[addr] = key_pair
        if add_count:
            self.key_count += 1


class SpendableKey():
    """
    SpendableKey defines a PublicPrivate key pair as useable
    by a TFChain wallet.
    """

    def __init__(self, public_key, private_key):
        assert isinstance(public_key, PublicKey)
        self._public_key = public_key
        assert isinstance(private_key, SigningKey)
        self._private_key = private_key

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key(self):
        return self._private_key

    def unlock_hash(self):
        return self._public_key.unlock_hash()

    def sign(self, hash):
        """
        Sign the given hash and return the public key used to sign.

        @param hash: hash to be signed
        """
        sig = self._private_key.sign(hash)
        return (sig, self._public_key)


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
        assert isinstance(value, int)
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
        assert isinstance(value, int)
        self._chain_height = int(value)

    @property
    def outputs(self):
        """
        Available (coin) outputs.
        """
        return self._outputs
    @property
    def outputs_spent(self):
        """
        Spent (coin) outputs.
        """
        return self._outputs_spent
    @property
    def outputs_unconfirmed(self):
        """
        Unconfirmed (coin) outputs, available for spending.
        """
        return self._outputs_unconfirmed
    @property
    def outputs_unconfirmed_spent(self):
        """
        Unconfirmed (coin) outputs that have already been spent.
        """
        return self._outputs_unconfirmed_spent

    @property
    def available_outputs(self):
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
        # TODO: figure out why sum doesn't return a Currency value
        return Currency(value=sum([co.value for co in self.available_outputs]))

    @property
    def locked(self):
        """
        Total available coins that are locked.
        """
        # TODO: figure out why sum doesn't return a Currency value
        if self.chain_time > 0 and self.chain_height > 0:
            return Currency(value=sum([co.value for co in self._outputs.values()
                if co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)]))
        else:
            return Currency(value=0) # impossible to know for sure without a complete context

    @property
    def unconfirmed(self):
        """
        Total unconfirmed coins, available for spending.
        """
        # TODO: figure out why sum doesn't return a Currency value
        if self.chain_time > 0 and self.chain_height > 0:
            return Currency(value=sum([co.value for co in self._outputs_unconfirmed.values()
                if not co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)]))
        else:
            return Currency(value=sum([co.value for co in self._outputs_unconfirmed.values()]))

    @property
    def unconfirmed_locked(self):
        """
        Total unconfirmed coins that are locked, and thus not available for spending.
        """
        # TODO: figure out why sum doesn't return a Currency value
        if self.chain_time > 0 and self.chain_height > 0:
            return Currency(value=sum([co.value for co in self._outputs_unconfirmed.values()
                if co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)]))
        else:
            return Currency(value=0) # impossible to know for sure without a complete context

    def fund(self, amount):
        """
        Fund the specified amount with the available outputs of this wallet's balance.
        """
        available_outputs = self.available_outputs
        available_outputs.sort(key=lambda co: co.value)
        collected = Currency(value=0)
        outputs = []
        for co in available_outputs:
            if co.value >= amount:
                outputs = [co]
                collected = co.value
                break
            collected += co.value
            outputs.append(co)
            if len(outputs) > 99:
                # to not reach the input limit
                collected -= outputs.pop(0).value
            if collected >= amount:
                break
        if collected < amount:
            raise InsufficientFunds("not enough funds available in the wallet to fund the requested amount")
        return (outputs, collected-amount)

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
        else: # unconfirmed outputs
            if spent:
                self._outputs_unconfirmed_spent[output.id] = output
                # delete from other output lists if prior registered
                self._outputs_unconfirmed.pop(output.id, None)
                self._outputs.pop(output.id, None)
                self._outputs_spent.pop(output.id, None)
            elif output.id not in self._outputs_spent and output.id not in self._outputs_unconfirmed_spent:
                self._outputs_unconfirmed[output.id] = output

    def _human_readable_balance(self):
        # report confirmed coins
        result = "{} available and {} locked".format(self.available.totft(with_unit=True), self.locked.totft(with_unit=True))
        # optionally report unconfirmed coins
        unconfirmed = self.unconfirmed
        unconfirmed_locked = self.unconfirmed_locked
        if unconfirmed > 0 or unconfirmed_locked > 0:
            result += "\nUnconfirmed: {} available {} locked".format(unconfirmed.totft(with_unit=True), unconfirmed_locked.totft(with_unit=True))
        unconfirmed_spent = Currency(value=sum([co.value for co in self._outputs_unconfirmed_spent.values()]))
        if unconfirmed_spent > 0:
            result += "\nUnconfirmed Balance Deduction: -{}".format(unconfirmed_spent.totft(with_unit=True))
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
        assert signature_count >= 1
        assert len(owners) >= signature_count
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
        assert isinstance(output.condition, ConditionMultiSignature)
        if not address in self._wallets:
            self._wallets[address] = MultiSigWalletBalance(
                owners=output.condition.unlockhashes,
                signature_count=output.condition.required_signatures)
        self._wallets[address].output_add(output, confirmed=confirmed, spent=spent)

    def __repr__(self):
        result = super().__repr__()
        for wallet in self.wallets.values():
            result += "\n\n" + wallet._human_readable_balance()
        return result
