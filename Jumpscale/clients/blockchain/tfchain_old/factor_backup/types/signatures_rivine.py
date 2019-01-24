"""
This modules defines types related to signatures

TODO: same names as in : /sandbox/code/github/threefoldtech/jumpscaleX/Jumpscale/clients/blockchain/tfchain/types/signatures_rivine.py

make sure there are methods on j.clients.tfchain.types.

ONLY use from j.clients.tfchain.types. in code further


"""

from clients.blockchain.rivine.encoding import binary

SIGEd25519 = 'ed25519'
SPECIFIER_SIZE = 16


class SiaPublicKeyFactory:
    """
    SiaPublicKeyFactory class
    """
    @staticmethod
    def from_string(pub_key_str):
        """
        Creates a SiaPublicKey from a string
        """
        algo, pub_key = pub_key_str.split(':')
        if algo == SIGEd25519:
            return Ed25519PublicKey(pub_key=bytearray.fromhex(pub_key))



class SiaPublicKey:
    """
    A SiaPublicKey is a public key prefixed by a Specifier. The Specifier
	indicates the algorithm used for signing and verification.
    """
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
        s = bytearray(SPECIFIER_SIZE)
        s[:len(self._algorithm)] = bytearray(self._algorithm, encoding='utf-8')
        key_value.extend(s)
        key_value.extend(binary.encode(self._pub_key, type_='slice'))
        return key_value


    @property
    def json(self):
        """
        Returns a json encoded version of the SiaPublicKey
        """
        return "{}:{}".format(self._algorithm, self._pub_key.hex())


class Ed25519PublicKey(SiaPublicKey):
    """
    Ed25519PublicKey returns pk as a SiaPublicKey, denoting its algorithm as Ed25519.
    """
    def __init__(self, pub_key):
        """
        Initialize new Ed25519PublicKey
        """
        super().__init__(algorithm=SIGEd25519, pub_key=pub_key)
