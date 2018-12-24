from Jumpscale import j
from .TLS import TLS

JSBASE = j.application.JSBaseClass


class TLSFactory(j.builder._BaseClass):
    """Factory class to deal with TLS, key and certificate generation"""

    def __init__(self):
        self.__jslocation__ = "j.tools.tls"
        JSBASE.__init__(self)
    # def getByInstance(self, instance='main'):
    #     """
    #     Get an instance of the TLS class
    #     This module use the cfssl AYS.
    #     """
    #     cfssl = None
    #     services = j.atyourservice.server.findServices(name='cfssl', instance=instance)
    #     if len(services) <= 0:
    #         j.events.opserror_critical(msg="Can't find cfssl service with instance name %s" % instance, category="cfssl.load")
    #     else:
    #         cfssl = services[0]

    #     return TLS(cfsslService=cfssl)

    def get(self, path=None):
        """
        Get an instance of the TLS class
        This module use the cfssl AYS.
        Path is the working directory where the certificate and key will be generated
        """
        return TLS(path=path)
