
from Jumpscale import j


class TFChainWallet(j.application.JSBaseConfigClass):
    """
    Tfchain Wallet object
    """
    _SCHEMATEXT = """
        @url = jumpscale.tfchain.wallet
        name* = "" (S)
        """

    def _init(self):
        j.shell()

class TFChainWallets(j.application.JSBaseConfigsClass):
    """
    Tfchain client object
    """
    _CHILDCLASS = TFChainWallet
    _name = "wallets"
