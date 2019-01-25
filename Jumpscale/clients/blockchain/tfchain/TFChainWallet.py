
from Jumpscale import j

class TFChainWallet(j.application.JSBaseConfigClass):
    """
    Tfchain Wallet object
    """
    _SCHEMATEXT = """
        @url = jumpscale.tfchain.wallet
        name* = "" (S)
        """

    @property
    def network_type(self):
        return self._parent._parent.network_type
