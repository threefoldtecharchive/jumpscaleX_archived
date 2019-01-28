from Jumpscale import j

from .unlockconditions import *
from .UnlockHash import UnlockHash

class TypesFactory(j.application.JSBaseClass):
    """
    A transaction factory class

    use through: j.clients.tfchain.types.

    """

    def fulfillment_get(self,fulfillment_dict):
        """
        Creates a fulfillment from a dict
        #TODO: is this supposed to be used directly from here, describe better what it does
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

    def unlockhash_get(self,unlock_type, hash):
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
        return UnlockHash(unlock_type=unlock_type,hash=hash)

    def condition_unlock_from_dict(self,condition_dict):
        """
        Creates an unlock condition object from a dictionary
        #TODO: need more explanation
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

    def condition_multisign_get(self,unlockhashes, min_nr_sig):
        """
        Initialize a new MultiSignatureCondition object

        @param unlockhashes: List of unlockhashes
        @param min_nr_sig: Minimum number of signatures required to fulfill this condition
        """
        return MultiSignatureCondition(unlockhashes=unlockhashes,min_nr_sig=min_nr_sig)

    def condition_atomicswap_get(self,sender, reciever, hashed_secret, locktime):
        """
        Initializes a new AtomicSwapCondition object
        """
        return AtomicSwapCondition(sender=sender,reciever=reciever,hashed_secret=hashed_secret,locktime=locktime)

    def condition_locktime_get(self,condition, locktime):
        """
        Initializes a new LockTimeCondition

        @param locktime: Identifies the height or timestamp until which this output is locked
        If the locktime is less then 500 milion it is to be assumed to be identifying a block height,
        otherwise it identifies a unix epoch timestamp in seconds

        @param condition: A condtion object that can be an UnlockHashCondition or a MultiSignatureCondition
        """
        return LockTimeCondition(condition=condition,locktime=locktime)

    def condition_unlockhash_get(self,unlockhash):
        """SingleSignatureFulfillment
        Initializes a new unlockhashcondition
        """
        return UnlockHashCondition(unlockhash)
