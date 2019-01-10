from .Pubsub import Pubsub
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class PubsubFactory(JSBASE):
    __jslocation__ = "j.sal_zos.pubsub"

    @staticmethod
    def get(loop, host, port=6379, password="", db=0, ctx=None,
            timeout=None, testConnectionAttempts=3, callback=None):
        """
        Get sal for pubsub
        Returns:
            the sal layer 
        """
        return Pubsub(loop, host, port, password, db, ctx, timeout, testConnectionAttempts, callback)

