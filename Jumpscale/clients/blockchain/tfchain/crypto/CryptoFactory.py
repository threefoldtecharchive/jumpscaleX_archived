from Jumpscale import j
from pyblake2 import blake2b

HASH_SIZE = 32

class CryptoFactory(j.application.JSBaseClass):
    """
    A transaction factory class

    use through: j.clients.tfchain.crypto.

    """

    def hash(self, data):
        """
        Hashes the input binary data using the blake2b algorithm

        @param data: Input data to be hashed
        @returns: Hashed value of the input data
        """
        return blake2b(data, digest_size=HASH_SIZE).digest()
