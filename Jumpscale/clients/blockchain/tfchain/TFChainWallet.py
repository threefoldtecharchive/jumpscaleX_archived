
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
        e.add(self.key_count-1)
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
