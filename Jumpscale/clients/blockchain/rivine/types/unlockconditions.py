"""
Unlockconditions module
"""

from JumpscaleLib.clients.blockchain.rivine.encoding import binary
from JumpscaleLib.clients.blockchain.rivine.types.unlockhash import UnlockHash
from JumpscaleLib.clients.blockchain.rivine.types.signatures import SiaPublicKeyFactory, Ed25519PublicKey

ATOMICSWAP_CONDITION_TYPE = bytearray([2])
MULTISIG_CONDITION_TYPE = bytearray([4])

# TODO:
# SUPPORT Conditions as well


class FulfillmentFactory:
    """
    FulfillmentFactory class
    """
    @staticmethod
    def from_dict(fulfillment_dict):
        """
        Creates a fulfillment from a dict
        """
        fulfillment = None
        if 'data' in fulfillment_dict:
            if 'type' in fulfillment_dict:
                if fulfillment_dict['type'] == 1:
                    pub_key = SiaPublicKeyFactory.from_string(fulfillment_dict['data']['publickey'])
                    fulfillment = SingleSignatureFulfillment(pub_key=pub_key)
                    if 'signature' in fulfillment_dict['data']:
                        fulfillment._signature = bytearray.fromhex(fulfillment_dict['data']['signature'])
                elif fulfillment_dict['type'] == 2:
                    pub_key = SiaPublicKeyFactory.from_string(fulfillment_dict['data']['publickey'])
                    fulfillment = AtomicSwapFulfillment(pub_key=pub_key, secret=fulfillment_dict['data'].get('secret'))
                    if 'signature' in fulfillment_dict['data']:
                        fulfillment._signature = bytearray.fromhex(fulfillment_dict['data']['signature'])
                elif fulfillment_dict['type'] == 3:
                    fulfillment = MultiSignatureFulfillment.from_dict(fulfillment_dict['data'])

        return fulfillment


class BaseFulFillment:
    """
    BaseFulFillment class
    """
    def __init__(self, pub_key=None):
        """
        Initializes a new BaseFulfillment object
        """
        self._type = bytearray()
        self._pub_key = pub_key
        self._signature = None
        self._extra_objects = None


    @property
    def json(self):
        """
        Returns a json encoded versoin of the Fulfillment
        """
        return {
            'type': binary.decode(self._type, type_=int),
            'data':{
                'publickey': self._pub_key.json,
                'signature': self._signature.hex() if self._signature else ''
            }
        }



    def sign(self, sig_ctx):
        """
        Sign the given fulfillment, which is to be done after all properties have been filled of the parent transaction.
        Should the Fulfillment already be signed, calling this method will return immediately.

        @param sig_ctx: Signature context should be a dictionary containing the secret key, input index, and transaction object
        """
        if self._signature:
            return
        sig_hash = sig_ctx['transaction'].get_input_signature_hash(input_index=sig_ctx['input_idx'],
                                                                    extra_objects=self._extra_objects)
        self._signature = sig_ctx['secret_key'].sign(sig_hash)


class MultiSignatureFulfillment:
    """
    MultiSignatureFulfillment class
    """
    def __init__(self):
        """
        Initializes new MultiSignatureFulfillment object
        """
        self._type = bytearray([3])
        self._pairs = []


    @classmethod
    def from_dict(cls, data):
        """
        Create a new MultiSignatureFulfillment from a dictionary
        """
        f = cls()
        if "pairs" in data:
            for pair in data['pairs']:
                if 'publickey' in pair and 'signature' in pair:
                    f.add_signature_pair(public_key=SiaPublicKeyFactory.from_string(pair['publickey']),
                                        signature=bytearray.fromhex(pair['signature']))
        return f


    def sign(self, sig_ctx):
        """
        Sign the given fulfillment, which is to be done after all properties have been filled of the parent transaction

        @param sig_ctx: Signature context should be a dictionary containing the secret key, input index, and transaction object
        """
        pk = sig_ctx['secret_key'].get_verifying_key()
        public_key = Ed25519PublicKey(pub_key=pk.to_bytes())
        sig_hash = sig_ctx['transaction'].get_input_signature_hash(input_index=sig_ctx['input_idx'],
                                                                    extra_objects=[public_key])
        signature = sig_ctx['secret_key'].sign(sig_hash)
        self.add_signature_pair(public_key=public_key,
                                signature=signature)



    def add_signature_pair(self, public_key, signature):
        """
        Adds a publickey signature pair
        """
        self._pairs.append({
            'publickey': public_key,
            'signature': signature
        })

    @property
    def json(self):
        """
        Returns a json encoded versoin of the MultiSignatureFulfillment
        """
        return {
            'type': binary.decode(self._type, type_=int),
            'data': {
                "pairs": [{'publickey': pair['publickey'].json,
                            'signature': pair['signature'].hex()} for pair in self._pairs]
            }
        }


class AtomicSwapFulfillment(BaseFulFillment):
    """
    AtomicSwapFulfillment class
    """
    def __init__(self, pub_key, secret=None):
        """
        Initializes a new AtomicSwapFulfillment object
        """
        super().__init__(pub_key=pub_key)
        self._secret = secret
        self._type = bytearray([2])
        self._extra_objects = [self._pub_key]
        if self._secret is not None:
            self._extra_objects.append(bytearray.fromhex(self._secret))


    @property
    def json(self):
        """
        Returns a json encoded versoin of the SingleSignatureFulfillment
        """
        result = super().json
        if self._secret:
            result['data']['secret'] = self._secret
        return result


class SingleSignatureFulfillment(BaseFulFillment):
    """
    SingleSignatureFulfillment class
    """
    def __init__(self, pub_key):
        """
        Initialzies new single singnature fulfillment class
        """
        super().__init__(pub_key=pub_key)
        self._type = bytearray([1])


class UnlockCondtionFactory:
    """
    UnlockCondtionFactory class
    """
    @staticmethod
    def from_dict(condition_dict):
        """
        Creates an unlock condition object from a dictionary
        """
        if 'data' in condition_dict:
            if 'type' in condition_dict:
                if condition_dict['type'] == 1:
                    return UnlockHashCondition(unlockhash=UnlockHash.from_string(condition_dict['data']['unlockhash']))
                elif condition_dict['type'] == 2:
                    return AtomicSwapCondition.from_dict(condition_dict['data'])
                elif condition_dict['type'] == 3:
                    return LockTimeCondition.from_dict(condition_dict['data'])
                elif condition_dict['type'] == 4:
                    return MultiSignatureCondition.from_dict(condition_dict['data'])


class MultiSignatureCondition:
    """
    A MultiSignatureCondition class
    """

    def __init__(self, unlockhashes, min_nr_sig):
        """
        Initialize a new MultiSignatureCondition object

        @param unlockhashes: List of unlockhashes
        @param min_nr_sig: Minimum number of signatures required to fulfill this condition
        """
        self._unlockhashes = unlockhashes
        self._min_nr_sig = min_nr_sig
        self._type = MULTISIG_CONDITION_TYPE

    @property
    def type(self):
        """
        Retruns the condition type
        """
        return self._type

    @property
    def data(self):
        """
        Retruns the binary format of the data on the condition
        """
        result = bytearray()
        result.extend(binary.encode(self._min_nr_sig))
        result.extend(binary.encode(len(self._unlockhashes)))
        for unlockhash in self._unlockhashes:
            result.extend(binary.encode(UnlockHash.from_string(unlockhash)))
        return result


    @property
    def binary(self):
        """
        Returns a binary encoded versoin of the MultiSignatureCondition
        """
        result = bytearray()
        result.extend(self._type)
        condition_binary = bytearray()
        condition_binary.extend(binary.encode(self._min_nr_sig))
        condition_binary.extend(binary.encode(len(self._unlockhashes)))
        for unlockhash in self._unlockhashes:
            condition_binary.extend(binary.encode(UnlockHash.from_string(unlockhash)))
        result.extend(binary.encode(condition_binary, type_='slice'))
        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the MultiSignatureCondition
        """
        return {
            'type': binary.decode(self._type, type_=int),
            'data': {
                'unlockhashes': self._unlockhashes,
                'minimumsignaturecount': self._min_nr_sig
            }
        }


    @classmethod
    def from_dict(cls, data):
        """
        Creates a new MultiSignatureCondition object from a dict
        """
        return cls(unlockhashes=data['unlockhashes'],
                   min_nr_sig=data['minimumsignaturecount'])


class AtomicSwapCondition:
    """
    AtomicSwapCondition class
    """
    def __init__(self, sender, reciever, hashed_secret, locktime):
        """
        Initializes a new AtomicSwapCondition object
        """
        self._sender = sender
        self._reciever = reciever
        self._hashed_secret = hashed_secret
        self._locktime = locktime
        self._type = ATOMICSWAP_CONDITION_TYPE


    @property
    def binary(self):
        """
        Returns a binary encoded versoin of the AtomicSwapCondition
        """
        result = bytearray()
        result.extend(self._type)
        # 106 size of the atomicswap condition in binary form
        result.extend(binary.encode(106))
        result.extend(binary.encode(UnlockHash.from_string(self._sender)))
        result.extend(binary.encode(UnlockHash.from_string(self._reciever)))
        result.extend(binary.encode(self._hashed_secret, type_='hex'))
        result.extend(binary.encode(self._locktime))

        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the AtomicSwapCondition
        """
        return {
            'type': binary.decode(self._type, type_=int),
            'data': {
                'timelock': self._locktime,
                'sender': self._sender,
                'receiver': self._reciever,
                'hashedsecret': self._hashed_secret
            }
        }


    @classmethod
    def from_dict(cls, data):
        """
        Creates a new AtomicSwapCondition object
        """
        return cls(sender=data['sender'],
                  reciever=data['receiver'],
                  hashed_secret=data['hashedsecret'],
                  locktime=data['timelock'])


class LockTimeCondition:
    """
    LockTimeCondition class
    """
    def __init__(self, condition, locktime):
        """
        Initializes a new LockTimeCondition

        @param locktime: Identifies the height or timestamp until which this output is locked
        If the locktime is less then 500 milion it is to be assumed to be identifying a block height,
        otherwise it identifies a unix epoch timestamp in seconds

        @param condition: A condtion object that can be an UnlockHashCondition or a MultiSignatureCondition
        """
        self._locktime = int(locktime)
        self._condition = condition
        self._type = bytearray([3])



    @property
    def binary(self):
        """
        Returns a binary encoded versoin of the LockTimeCondition
        """
        result = bytearray()
        result.extend(self._type)
        # encode the length of all properties: len(locktime) = 8 + len(binary(condition)) - 8
        # the -8 in the above statement is due to the fact that we do not need to include the length of the interal condition's data
        result.extend(binary.encode(len(self._condition.binary)))
        result.extend(binary.encode(self._locktime))
        result.extend(self._condition.type)
        result.extend(binary.encode(self._condition.data))
        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the LockTimeCondition
        """
        result = {
            'type': binary.decode(self._type, type_=int),
            'data': {
                'locktime': self._locktime,
                'condition': {},
            }
        }
        if self._condition:
            result['data']['condition'] = self._condition.json
        return result

    @classmethod
    def from_dict(cls, data):
        """
        Creates a new LockTimeCondition from a dict
        """
        innner_condtion = UnlockCondtionFactory.from_dict(data['condition'])
        return cls(condition=innner_condtion, locktime=data['locktime'])


class UnlockHashCondition:
    """
    UnlockHashCondition class
    """
    def __init__(self, unlockhash):
        """SingleSignatureFulfillment
        Initializes a new unlockhashcondition
        """
        self._unlockhash = unlockhash
        self._type = bytearray([1])
        self._unlockhash_size = 33



    @property
    def type(self):
        """
        Returns the unlock type
        """
        return self._type


    @property
    def data(self):
        """
        Returns the condtion data being the unlockhash in this condition type
        """
        return self._unlockhash


    @property
    def binary(self):
        """
        Returns a binary encoded version of the unlockhashcondition
        """
        result = bytearray()
        result.extend(self._type)
        # add the size of the unlockhash
        result.extend(binary.encode(self._unlockhash_size))
        result.extend(binary.encode(self._unlockhash))
        return result


    @property
    def json(self):
        """
        Returns a json encoded version of the UnlockHashCondition
        """
        return {
            'type': binary.decode(self._type, type_=int),
            'data': {
                'unlockhash': str(self._unlockhash)
            }
        }
