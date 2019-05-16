from .Hypervisor import Hypervisor
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class HypervisorFactory(JSBASE):
    __jslocation__ = "j.sal_zos.hypervisor"

    @staticmethod
    def get(node):
        """
        Get sal for Hypervisor
        Returns:
            the sal layer 
        """
        return Hypervisor(node)
