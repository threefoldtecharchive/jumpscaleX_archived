
from Jumpscale import j

from ed25519 import SigningKey

from .types.CryptoTypes import PublicKey, UnlockHash

class TFChainWallet(j.application.JSBaseConfigClass):
    """
    Tfchain Wallet object
    """
    _SCHEMATEXT = """
        @url = jumpscale.tfchain.wallet
        name* = "" (S)
        seed = "" (S)
        key_count = 1 (I)
        """

    def _init(self):
        self._key_pairs = {}
        self._primary_address = ''
 
    def _data_trigger_new(self):
        if self.seed == "":
            self.seed = j.data.encryption.mnemonic.generate(strength=256)
        if self.key_count < 1:
            self.key_count = 1
        keys_to_generate = self.key_count
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

    def _key_pair_new(self):
        e = j.data.rivine.encoder_sia_get()
        e.add_array(self.seed_entropy)
        e.add(self.key_count-1)
        seed_hash = bytes.fromhex(j.data.hash.blake2_string(e.data))
        private_key = SigningKey(seed_hash)
        public_key = private_key.get_verifying_key()
        
        key_pair = SpendableKey(
            public_key = j.clients.tfchain.types.public_key_new(hash=public_key.to_bytes()),
            private_key = private_key)
        self._key_pairs[str(key_pair.unlock_hash())] = key_pair
        self.key_count += 1

        return key_pair


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
