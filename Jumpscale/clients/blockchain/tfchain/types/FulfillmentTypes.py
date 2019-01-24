from Jumpscale import j

from .BaseDataType import BaseDataTypeClass
from .CryptoTypes import PublicKey
from .PrimitiveTypes import BinaryData

_FULFULLMENT_TYPE_SINGLE_SIG = 1
_FULFILLMENT_TYPE_ATOMIC_SWAP = 2
_FULFILLMENT_TYPE_MULTI_SIG = 3

class FulfillmentFactory(j.application.JSBaseClass):
    """
    Fulfillment Factory class
    """
    def from_json(self, obj):
        ft = obj.get('type', 0)
        if ft == _FULFULLMENT_TYPE_SINGLE_SIG:
            return FulfillmentSingleSignature.from_json(obj)
        if ft == _FULFILLMENT_TYPE_MULTI_SIG:
            return FulfillmentMultiSignature.from_json(obj)
        if ft == _FULFILLMENT_TYPE_ATOMIC_SWAP:
            return FulfillmentAtomicSwap.from_json(obj)
        raise ValueError("unsupport fulfillment type {}".format(type))

    def single_signature_new(self, pub_key=None, signature=None):
        """
        Create a new single signature fulfillment,
        used to unlock an UnlockHash Condition of type 1.
        """
        return FulfillmentSingleSignature(pub_key=pub_key, signature=signature)

    def atomic_swap_new(self, pub_key=None, signature=None, secret=None):
        """
        Create a new atomic swap fulfillment,
        used to unlock an atomic swap condition.
        """
        return FulfillmentAtomicSwap(pub_key=pub_key, signature=signature, secret=secret)

    def multi_signature_new(self, pairs=None):
        """
        Create a new multi signature fulfillment,
        used to unlock a multi signature condition.
        """
        return FulfillmentMultiSignature(pairs=pairs)


    def test(self):
        """
        js_shell 'j.clients.tfchain.types.fulfillments.test()'
        """

        # single signature fulfillments are supported
        ss_json = {"type":1,"data":{"publickey":"ed25519:dda39750fff2d869badc797aaad1dea8c6bcf943879421c58ac8d8e2072d5b5f","signature":"818dfccee2cb7dbe4156169f8e1c5be49a3f6d83a4ace310863d7b3b698748e3e4d12522fc1921d5eccdc108b36c84d769a9cf301e969bb05db1de9295820300"}}
        assert self.from_json(ss_json).json() == ss_json

        # atomic swap fulfillments are supported
        as_json = {"type":2,"data":{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab","secret":"def789def789def789def789def789dedef789def789def789def789def789de"}}
        assert self.from_json(as_json).json() == as_json

        # multi signature fulfillments are supported
        ms_json = {"type":3,"data":{"pairs":[{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab"},{"publickey":"ed25519:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","signature":"abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdefab"}]}}
        assert self.from_json(ms_json).json() == ms_json


from abc import abstractmethod

class FulfillmentBaseClass(BaseDataTypeClass):
    @classmethod
    def from_json(cls, obj):
        ff = cls()
        assert ff.type == obj.get('type', 0)
        ff.from_json_data_object(obj.get('data', {}))
        return ff

    @property
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def from_json_data_object(self, data):
        pass

    @abstractmethod
    def json_data_object(self):
        pass

    def json(self):
        return {
            'type': self.type,
            'data': self.json_data_object(),
        }

    # binary encoding is not supported for fulfillments, as this client does not require it
    def sia_binary_encode(self, encoder):
        raise Exception("sia binary encoding not supported for fulfillments by this client")
    def rivine_binary_encode(self, encoder):
        raise Exception("rivine binary encoding not supported fulfillments by this client")


class FulfillmentSingleSignature(FulfillmentBaseClass):
    """
    SingleSignature Fulfillment, used to unlock
    an UnlockHash Condition of type 1.
    """

    def __init__(self, pub_key=None, signature=None):
        self._pub_key = None
        self.public_key = pub_key
        self._signature = None
        self.signature = signature


    @property
    def type(self):
        return _FULFULLMENT_TYPE_SINGLE_SIG

    @property
    def public_key(self):
        return self._pub_key
    @public_key.setter
    def public_key(self, value):
        if not value:
            self._pub_key = PublicKey()
        else:
            assert type(value) is PublicKey
            self._pub_key = value
    
    @property
    def signature(self):
        return self._signature
    @signature.setter
    def signature(self, value):
        if not value:
            self._signature = BinaryData()
        elif type(value) is BinaryData:
            self._signature = value
        else:
            self._signature = BinaryData(value=value)
    
    def from_json_data_object(self, data):
        self._pub_key = PublicKey.from_json(data['publickey'])
        self._signature = BinaryData.from_json(data['signature'])

    def json_data_object(self):
        return {
            'publickey': self._pub_key.json(),
            'signature': self._signature.json()
        }


class FulfillmentMultiSignature(FulfillmentBaseClass):
    """
    MultiSignature Fulfillment, used to unlock
    a MultiSignature Condition.
    """

    def __init__(self, pairs=None):
        self._pairs = []
        if pairs:
            for public_key, signature in pairs:
                self.add_pair(public_key, signature)

    @property
    def type(self):
        return _FULFILLMENT_TYPE_MULTI_SIG

    @property
    def pairs(self):
        return self._pairs

    def add_pair(self, public_key, signature):
        if not public_key:
            public_key = PublicKey()
        else:
            assert type(public_key) is PublicKey
        if not signature:
            signature = BinaryData()
        elif not type(signature) is BinaryData:
            signature = BinaryData(value=signature)
        self._pairs.append((public_key, signature))

    def from_json_data_object(self, data):
        self._pairs = []
        for pair in data['pairs']:
            pk = PublicKey.from_json(pair['publickey'])
            sig = BinaryData.from_json(pair['signature'])
            self._pairs.append((pk, sig))

    def json_data_object(self):
        return {
            'pairs': [{
                'publickey': pk.json(),
                'signature': sig.json(),
            } for pk, sig in self._pairs],
        }

# Legacy AtomicSwap Fulfillments are not supported,
# as these are not used on any active TFChain network

class FulfillmentAtomicSwap(FulfillmentBaseClass):
    """
    AtomicSwap Fulfillment, used to unlock an AtomicSwap Condition.
    """

    def __init__(self, pub_key=None, signature=None, secret=None):
        self._pub_key = None
        self.public_key = pub_key
        self._signature = None
        self.signature = signature
        self._secret = None
        self.secret = secret

    @property
    def type(self):
        return _FULFILLMENT_TYPE_ATOMIC_SWAP

    @property
    def public_key(self):
        return self._pub_key
    @public_key.setter
    def public_key(self, value):
        if not value:
            self._pub_key = PublicKey()
        else:
            assert type(value) is PublicKey
            self._pub_key = value

    @property
    def signature(self):
        return self._signature
    @signature.setter
    def signature(self, value):
        if not value:
            self._signature = BinaryData()
        elif type(value) is BinaryData:
            self._signature = value
        else:
            self._signature = BinaryData(value=value)

    @property
    def secret(self):
        return self._secret
    @secret.setter
    def secret(self, value):
        if not value:
            self._secret = BinaryData()
        elif type(value) is BinaryData:
            self._secret = value
        else:
            self._secret = BinaryData(value=value)

    def from_json_data_object(self, data):
        self._pub_key = PublicKey.from_json(data['publickey'])
        self._signature = BinaryData.from_json(data['signature'])
        self._secret = BinaryData.from_json(data['secret'])

    def json_data_object(self):
        return {
            'publickey': self._pub_key.json(),
            'signature': self._signature.json(),
            'secret': self._secret.json()
        }
