"""
Holds constants values
"""

HASH_SIZE = 32
MINER_PAYOUT_MATURITY_WINDOW = 144
ADDRESS_TYPE_SIZE = 2
WALLET_ADDRESS_TYPE = bytearray([1])
SWAP_ADDRESS_TYPE = bytearray([2])
HASTINGS_TFT_VALUE = 1000000000
MINIMUM_TRANSACTION_FEE = int(.1 * HASTINGS_TFT_VALUE)
ATOMICSWAP_SECRET_SIZE = 32
# this is the value if the locktime is less than it, it means that the locktime should be interpreted as the chain height lock instead of the timestamp
TIMELOCK_CONDITION_HEIGHT_LIMIT = 5000000
UNLOCKHASH_TYPE = 'unlockhash'
NR_OF_EXTRA_ADDRESSES_TO_CHECK = 10

NIL_UNLOCK_HASH = '0'*78