from .Primitives import Primitives
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class PrimitivesFactory(JSBASE):
    __jslocation__ = "j.sal_zos.primitives"

    @staticmethod
    def get(node):
        """
        Get sal for zos primitives
        Returns:
            the sal layer 
        """
        return Primitives(node)

