from Jumpscale import j

from .BaseDataType import BaseDataTypeClass
from .PrimitiveTypes import Hash
from .errors import InvalidPublicKeySpecifier
from .ConditionTypes import UnlockHash, UnlockHashType

from enum import IntEnum

_SIG_Ed25519 = 'ed25519'

class PublicKeySpecifier(IntEnum):
    NIL = 0
    ED25519 = 1

    @classmethod
    def from_json(cls, obj):
        if not obj:
            return PublicKeySpecifier.NIL
        if obj == _SIG_Ed25519:
            return PublicKeySpecifier.ED25519
        raise InvalidPublicKeySpecifier("{} is an invalid Public Key specifier".format(obj))

    def __str__(self):
        if self == PublicKeySpecifier.ED25519:
            return _SIG_Ed25519
        return ""

    __repr__ = __str__

    json = __str__


class PublicKey(BaseDataTypeClass):
    """
    A PublicKey is a public key prefixed by a Specifier. The Specifier
	indicates the algorithm used for signing and verification.
    The other part of the PublicKey is the hash itself.
    """

    def __init__(self, specifier=None, hash=None):
        self._specifier = PublicKeySpecifier.NIL
        self._hash = j.clients.tfchain.types.hash_new()

        self.specifier = specifier
        self.hash = hash

    @classmethod
    def from_json(cls, obj):
        if not obj:
            return cls()
        assert type(obj) is str
        parts = obj.split(sep=':', maxsplit=2)
        assert len(parts) == 2
        pk = cls()
        pk._specifier = PublicKeySpecifier.from_json(parts[0])
        pk._hash = Hash.from_json(parts[1])
        return pk
    
    @property
    def specifier(self):
        return self._specifier
    @specifier.setter
    def specifier(self, value):
        if value == None:
            value = PublicKeySpecifier.NIL
        else:
            assert isinstance(value, PublicKeySpecifier)
        self._specifier = value

    @property
    def hash(self):
        return self.hash
    @hash.setter
    def hash(self, value):
        self._hash.value = value

    def __str__(self):
        return str(self._specifier) + ':' + str(self._hash)
    
    __repr__ = __str__
    
    json = __str__

    def unlock_hash(self):
        """
        Return the unlock hash generated from this public key.
        """
        e = j.data.rivine.encoder_rivine_get()
        e.add_int8(int(self._specifier))
        e.add(self._hash)
        hash = bytearray.fromhex(j.data.hash.blake2_string(e.data))
        return UnlockHash(type=UnlockHashType.PUBLIC_KEY, hash=hash)

    @staticmethod
    def _pad_specifier(specifier):
        _SPECIFIER_SIZE = 16
        return specifier.encode('utf-8') + b'\x00'*(_SPECIFIER_SIZE-len(specifier))

    def sia_binary_encode(self, encoder):
        """
        Encode this binary data according to the Sia Binary Encoding format.
        """
        encoder.add_array(PublicKey._pad_specifier(self._specifier))
        encoder.add_slice(self._hash)
    
    def rivine_binary_encode(self, encoder):
        """
        Encode this binary data according to the Rivine Binary Encoding format.
        """
        encoder.add_int8(int(self._specifier))
        encoder.add(self._hash)
