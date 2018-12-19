"""
This modules defines types related to signatures
"""

from clients.blockchain.rivine.encoding import binary as rbinary
from clients.blockchain.tfchain.encoding import binary
from clients.blockchain.rivine.types import signatures
from clients.blockchain.rivine import utils
from clients.blockchain.rivine.types.unlockhash import UnlockHash, UNLOCK_TYPE_PUBKEY

from enum import IntEnum

class InvalidSiaPublicKeySpecifier(Exception):
    """
    InvalidSiaPublicKeySpecifier error
    """

class SiaPublicKeySpecifier(IntEnum):
    NIL = 0
    ED25519 = 1

    @classmethod
    def from_string(cls, algo_str):
        if not algo_str:
            return SiaPublicKeySpecifier.NIL
        if algo_str == signatures.SIGEd25519:
            return SiaPublicKeySpecifier.ED25519
        raise InvalidSiaPublicKeySpecifier("{} is an invalid Sia Public Key specifier".format(algo_str))

    def __str__(self):
        if self == SiaPublicKeySpecifier.ED25519:
            return signatures.SIGEd25519
        return ""

    def __repr__(self):
        """
        Override so we have nice output in js shell if the object is not assigned
        without having to call the print method.
        """
        return str(self)

    @property
    def binary(self):
        """
        Encodes the public key specifier into binary format
        """
        return binary.IntegerBinaryEncoder.encode(self)

    @property
    def binary_specifier(self):
        s = bytearray(signatures.SPECIFIER_SIZE)
        if self == SiaPublicKeySpecifier.ED25519:
            s[:len(signatures.SIGEd25519)] = bytearray(signatures.SIGEd25519, encoding='utf-8')
        return s


class SiaPublicKey:
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

    @property
    def binary(self):
        """
        Encodes the public key into binary format
        """
        key_value = bytearray()
        key_value.extend(binary.IntegerBinaryEncoder.encode(self._algorithm, _kind='uint8'))
        key_value.extend(self._pub_key)
        return key_value

    @property
    def rivine_binary(self):
        """
        Encodes the public key into (rivine) binary format
        """
        key_value = bytearray()
        key_value.extend(self._algorithm.binary_specifier)
        key_value.extend(rbinary.encode(self._pub_key, type_='slice'))
        return key_value
    
    def __str__(self):
        return "{}:{}".format(str(self._algorithm), self._pub_key.hex())

    def __repr__(self):
        """
        Override so we have nice output in js shell if the object is not assigned
        without having to call the print method.
        """
        return str(self)

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
