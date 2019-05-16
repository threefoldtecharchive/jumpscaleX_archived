from Jumpscale import j
from .Dnsmasq import DNSMasq

JSBASE = j.application.JSBaseClass


class DnsmasqFactory(JSBASE):
    """Factory class to deal with Dnsmasq"""

    def __init__(self):
        self.__jslocation__ = "j.sal.dnsmasq"
        JSBASE.__init__(self)

    def get(self, path="/etc/dnsmasq"):
        """Get an instance of the Dnsmasq class
        :param path: path of the dnsmasq configuration directory, defaults to /etcd/dnsmasq/
        :type path: string, optional
        :return: Dnsmasq instance
        :rtype: Dnsmasq class
        """
        return DNSMasq(path=path)
