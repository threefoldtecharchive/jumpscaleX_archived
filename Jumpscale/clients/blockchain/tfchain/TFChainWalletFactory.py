from Jumpscale import j

from .TFChainWallet import TFChainWallet


class TFChainWalletFactory(j.application.JSBaseConfigsClass):
    """
    Tfchain client object
    """

    _CHILDCLASS = TFChainWallet
    _name = "wallets"
