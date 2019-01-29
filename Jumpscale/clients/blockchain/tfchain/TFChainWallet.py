
from Jumpscale import j

from ed25519 import SigningKey

from .types.CryptoTypes import PublicKey, UnlockHash
from .types.errors import ExplorerNoContent

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
        # TODO: support extra address key scanning, this call is the perfect opportunity to try that
        addresses = self.addresses
        balance = WalletsBalance()
        # collect info for all personal addresses
        multisig_addresses = []
        for address in addresses:
            try:
                # collect the inputs/outputs linked to this address for all found transactions
                result = self._parent._parent.unlockhash_get(address)
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
                result = self._parent._parent.unlockhash_get(address)
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
        info = self._parent._parent.blockchain_info_get()
        balance.chain_height = info.height
        balance.chain_time = info.timestamp
        # return the balance
        return balance

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
    def available(self):
        """
        Total available coins.
        """
        if self.chain_time > 0 and self.chain_height > 0:
            return sum([co.value for co in self._outputs.values()
                if not co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)])
        else:
            return sum([co.value for co in self._outputs.values()])

    @property
    def locked(self):
        """
        Total available coins that are locked.
        """
        if self.chain_time > 0 and self.chain_height > 0:
            return sum([co.value for co in self._outputs.values()
                if co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)])
        else:
            return 0 # impossible to know for sure without a complete context

    @property
    def unconfirmed(self):
        """
        Total unconfirmed coins, available for spending.
        """
        if self.chain_time > 0 and self.chain_height > 0:
            return sum([co.value for co in self._outputs_unconfirmed.values()
                if not co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)])
        else:
            return sum([co.value for co in self._outputs_unconfirmed.values()])

    @property
    def unconfirmed_locked(self):
        """
        Total unconfirmed coins that are locked, and thus not available for spending.
        """
        if self.chain_time > 0 and self.chain_height > 0:
            return sum([co.value for co in self._outputs_unconfirmed.values()
                if co.condition.lock.locked_check(time=self.chain_time, height=self.chain_height)])
        else:
            return 0 # impossible to know for sure without a complete context

    def output_add(self, output, confirmed=True, spent=False):
        """
        Add an output to the Wallet's balance.
        """
        if confirmed: # confirmed outputs
            if output.id in self._outputs_spent:
                return # nothing to do, already registered as spent
            if spent:
                self._outputs_spent[output.id] = output
                if output.id in self._outputs: # delete from available outputs if prior registered
                    del self._outputs[output.id]
            else:
                self._outputs[output.id] = output
        else: # unconfirmed outputs
            if output.id in self._outputs_unconfirmed_spent:
                return # nothing to do, already registered as spent
            if spent:
                self._outputs_unconfirmed_spent[output.id] = output
                if output.id in self._outputs_unconfirmed: # delete from unconfirmed outputs if prior registered
                    del self._outputs_unconfirmed[output.id]
            else:
                self._outputs_unconfirmed[output.id] = output

    def _human_readable_balance(self):
        # report confirmed coins
        result = "{} TFT available and {} TFT locked".format(self.available, self.locked)
        # optionally report unconfirmed coins
        unconfirmed = self.unconfirmed
        unconfirmed_locked = self.unconfirmed_locked
        if unconfirmed > 0 or unconfirmed_locked > 0:
            result += "\nUnconfirmed: {} TFT available and {} TFT locked".format(unconfirmed, unconfirmed_locked)
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
