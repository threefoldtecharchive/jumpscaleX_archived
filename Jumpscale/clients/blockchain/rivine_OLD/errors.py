"""
Define Exceptions
"""

class RESTAPIError(Exception):
    """
    RESTAPI Error
    """


class BackendError(Exception):
    """
    Error representing a problem with the content of backend response
    """

class InsufficientWalletFundsError(Exception):
    """
    Error representing an insufficient wallet funds while creating a transaction
    """

class NonExistingOutputError(Exception):
    """
    Error representing a non-existing output referenced in a transaction
    """

class NotEnoughSignaturesFound(Exception):
    """
    Error representing a lack of enough keys to satisfies the number of required signatures
    """

class InvalidUnlockHashChecksumError(Exception):
    """
    Invalid unlockhash checksum error
    """

class InvalidAtomicswapContract(Exception):
    """
    InvalidAtomicswapContract error
    """

class AtomicSwapError(Exception):
    """
    AtomicSwapError error
    """

class WalletAlreadyExistsException(Exception):
    """
    Error since the wallet name is already used.
    """
    def __init__( self, wallet_name):
        super().__init__('Wallet "{0}" already exists, remove with j.clients.tfchain.delete("{0}")'.format( wallet_name))
