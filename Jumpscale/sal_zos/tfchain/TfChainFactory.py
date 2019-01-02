from .TfChain import TfChain
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class TfChainFactory(JSBASE):
    __jslocation__ = "j.sal_zos.tfchain"

    @staticmethod
    def get():
        """
        Get sal for tfchain
        Returns:
            the sal layer 
        """
        return TfChain()

