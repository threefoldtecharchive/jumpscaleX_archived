"""
AtomicSwap Types.
"""


from Jumpscale import j

from datetime import datetime

from .PrimitiveTypes import Hash, BinaryData
from .CompositionTypes import CoinOutput
from .ConditionTypes import ConditionAtomicSwap


class AtomicSwapContract():
    def __init__(self, coinoutput, unspent=True):
        """
        Creates a ReadOnly AtomicSwap contract for consumption purposes.
        """
        if not isinstance(coinoutput, CoinOutput):
            raise TypeError("expected coin output to be a CoinOutput, not to be of type {}".format(type(coinoutput)))
        if not isinstance(coinoutput.condition, ConditionAtomicSwap):
            raise TypeError("expected an atomic swap condition for the CoinOutput, not a condition of type {}".format(type(coinoutput.condition)))
        self._id = coinoutput.id
        self._condition = coinoutput.condition
        self._value = coinoutput.value
        if not isinstance(unspent, bool):
            raise TypeError("unspent status is expected to be of type bool, not {}".format(type(unspent)))
        self._unspent = unspent

    @property 
    def outputid(self):
        """
        The identifier of the (coin) output to which this Atomic Swap contract is attached.
        """
        return self._id  

    @property
    def sender(self):
        """
        The address of the wallet that can refund this Atomic Swap contract's value,
        given the contract has been unlocked and is available for refunds.
        """
        return self._condition.sender  
    @property
    def receiver(self):
        """
        The address of the wallet that can redeem this Atomic Swap contract's value,
        given they know the secret that matches this contract's secret hash.
        """
        return self._condition.receiver   
    @property
    def secret_hash(self):
        """
        Secret Hash of the Atomic Swap contract,
        a blake2b hash of the secret that is needed to redeem it.
        """
        return self._condition.hashed_secret

    @property
    def refund_timestamp(self):
        """
        The (UNIX epoch seconds) timestamp that
        identifies when the contract is ready for refund.
        """
        return self._condition.lock_time

    @property
    def amount(self):
        """
        Value (in TFT Currency) that the AtomicSwap Contract contains.
        """
        return self._value

    @property
    def unspent(self):
        """
        True if the contract has not been spent yet, False otherwise.
        """
        return self._unspent

    def verify_secret(self, secret):
        """
        Verifies the given secret is a valid value and
        matches the secret hash of this Atomic Swap Contract.

        Returns True if the secret has been verified succesfully, False otherwise.
        """
        if not isinstance(secret, BinaryData):
            raise TypeError("secret is expected to be of type BinaryData, not {}".format(type(secret)))
        if not len(secret.value) != 32:
            raise ValueError("secret is expected to have a byte length of 32, not {}".format(len(secret.value)))
        secret_hash = BinaryData(value=bytes.fromhex(j.data.hash.blake2_string(secret.value)))
        return self.secret_hash == secret_hash

    def __repr__(self):
        if self.unspent:
            time = int(datetime.now().timestamp())
            refund_time = j.data.time.epoch2HRDateTime(self.refund_timestamp)
            if time >= self.refund_timestamp:
                status_desc = "Refund is available since {}.".format(refund_time)
            else:
                duration = j.data.types.duration.toString(self.refund_timestamp-time)
                status_desc = "Refund available at {} (in: {}).".format(refund_time, duration)
        else:
            status_desc = "Spent and no longer available."
        return j.core.text.strip("""
        Atomic Swap Contract {}:
        {}
        Value: {}
        Sender: {}
        Receiver: {}
        Secret Hash: {}
        """.format(str(self.outputid), status_desc, self.amount.str(with_unit=True), str(self.sender), str(self.receiver), str(self.secret_hash)))
