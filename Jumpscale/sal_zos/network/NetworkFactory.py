from .Network import Network
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class NetworkFactory(JSBASE):
    __jslocation__ = "j.sal_zos.network"

    @staticmethod
    def get(node):
        """
        Get sal for Network
        Returns:
            the sal layer 
        """
        return Network(node)

