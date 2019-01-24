"""
This modules defines types related to signatures
make sure there are methods on j.clients.tfchain.types.
"""

from Jumpscale import j

from errors import InvalidSiaPublicKeySpecifier
from enum import IntEnum

SIGEd25519 = 'ed25519'

def _pad_specifier(specifier):
    _SPECIFIER_SIZE = 16
    return specifier.encode('utf-8') + b'\x00'*(_SPECIFIER_SIZE-len(specifier))

class SiaPublicKeySpecifier(IntEnum, j.data.rivine.BaseRivineObjectEncoder, j.data.rivine.BaseSiaObjectEncoder):
    NIL = 0
    ED25519 = 1

    @classmethod
    def from_string(cls, algo_str):
        if not algo_str:
            return SiaPublicKeySpecifier.NIL
        if algo_str == SIGEd25519:
            return SiaPublicKeySpecifier.ED25519
        raise InvalidSiaPublicKeySpecifier("{} is an invalid Sia Public Key specifier".format(algo_str))

    def __str__(self):
        if self == SiaPublicKeySpecifier.ED25519:
            return SIGEd25519
        return ""

    __repr__ = __str__

    def rivine_binary_encode(self, encoder):
        encoder.add_int8(int(self))

    def sia_binary_encode(self, encoder):
        if self == SiaPublicKeySpecifier.ED25519:
            encoder.add(_pad_specifier(SIGEd25519))
        else:
            encoder.add(_pad_specifier(''))


class SiaPublicKey(j.data.rivine.BaseRivineObjectEncoder, j.data.rivine.BaseSiaObjectEncoder):
    """
    A SiaPublicKey is a public key prefixed by a Specifier. The Specifier
	indicates the algorithm used for signing and verification.
    """

    @classmethod
    def from_string(cls, pub_key_str):
        """
        Creates a SiaPublicKey from a string
        """
        algo, pub_key = pub_key_str.split(':')
        return cls(algorithm=SiaPublicKeySpecifier.from_string(algo), pub_key=bytearray.fromhex(pub_key))

    def __init__(self, algorithm, pub_key):
        """
        Initialize new SiaPublicKey
        """
        self._algorithm = algorithm
        self._pub_key = pub_key

    def rivine_binary_encode(self, encoder):
        encoder.add(self._algorithm)
        encoder.add_array(self._pub_key)

    def sia_binary_encode(self, encoder):
        encoder.add_all(self._algorithm, self._pub_key)
    
    def __str__(self):
        return "{}:{}".format(str(self._algorithm), self._pub_key.hex())

    __repr__ = __str__

    @property
    def json(self):
        """
        Returns a json encoded version of the SiaPublicKey
        """
        return str(self)

    @property
    def unlock_hash(self):
        encoded_pub_key = self.rivine_binary
        hash = utils.hash(encoded_pub_key, encoding_type='slice')
        return UnlockHash(unlock_type=UNLOCK_TYPE_PUBKEY, hash=hash)
