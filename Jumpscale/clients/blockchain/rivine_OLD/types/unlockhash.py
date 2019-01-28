"""
Modules defines the unlockhash types
"""

from pyblake2 import blake2b
from clients.blockchain.rivine import utils
from clients.blockchain.rivine.encoding import binary

UNLOCK_TYPE_PUBKEY = bytearray([1])
UNLOCK_TYPE_ATOMICSWAP = bytearray([2])
UNLOCK_TYPE_MULTISIG = bytearray([3])
UNLOCKHASH_SIZE = 32
UNLOCKHASH_CHECKSUM_SIZE = 6
UNLOCKHASH_TYPE_ZISE = 1

class UnlockHash:
    """
    An UnlockHash is a specially constructed hash of the UnlockConditions type.
	"Locked" values can be unlocked by providing the UnlockConditions that hash
	to a given UnlockHash. See SpendConditions.UnlockHash for details on how the
	UnlockHash is constructed.
	UnlockHash struct {
		Type UnlockType
		Hash crypto.Hash
	}
    """
    def __init__(self, unlock_type, hash):
        """
        Initialize new unlockhash

        @param unlock_type: The type of the unlock for this unlockhash, the client only support unlocktype 0x01 for public keys unlock type
        @param hash: Hashed value of the input lock
        """
        self._unlock_type = unlock_type
        self._hash = hash


    def __str__(self):
        """
        String representation of UnlockHash object
        """
        uh_checksum = utils.hash([self._unlock_type, self._hash])
        return '{}{}{}'.format(self._unlock_type.hex(), self._hash.hex(), uh_checksum[:UNLOCKHASH_CHECKSUM_SIZE].hex())


    def __repr__(self):
        """
        Calls __str__
        """
        return str(self)


    @property
    def binary(self):
        """
        Returns a binary encoded unlockhash
        """
        result = bytearray()
        result.extend(self._unlock_type)
        result.extend(binary.encode(self._hash))
        return result

    @classmethod
    def from_string(cls, ulh_str):
        """
        Returns an unlockhash object from a string
        """
        if len(ulh_str) == (UNLOCKHASH_SIZE * 2) + (UNLOCKHASH_TYPE_ZISE * 2) + (UNLOCKHASH_CHECKSUM_SIZE * 2):
            ul_type, ulh, ulh_checksum = ulh_str[:UNLOCKHASH_TYPE_ZISE*2], ulh_str[UNLOCKHASH_TYPE_ZISE*2: UNLOCKHASH_TYPE_ZISE*2 + UNLOCKHASH_SIZE*2], ulh_str[UNLOCKHASH_TYPE_ZISE*2 + UNLOCKHASH_SIZE*2:]
            return cls(unlock_type=bytearray.fromhex(ul_type), hash=bytearray.fromhex(ulh))
