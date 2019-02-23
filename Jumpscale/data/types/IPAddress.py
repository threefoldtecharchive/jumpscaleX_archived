from .PrimitiveTypes import String
from .TypeBaseClasses import *
from Jumpscale import j

from ipaddress import IPv4Address, IPv6Address
from ipaddress import AddressValueError, NetmaskValueError

#TODO: *1

class IPAddressObject(TypeBaseObjClass):

    def __init__(self, val):
        raise RuntimeError("need to be implemented")
        self._jstype = j.data.types.ipaddr
        self._val = val
        val = j.data.types.string.clean(val)

        self._md5 = j.data.hash.md5_string(str(self))  # so it has the default as well

        j.data.types.ipaddrs[self._md5] = self

        # self._jumpscale_location = "j.data.types.ipaddrs['%s']" % self._md5

        try:
            self._val = IPv4Address(val)
        except (AddressValueError, NetmaskValueError):
            pass

        if not self._val:
            try:
                self._val = IPv6Address(val)
            except (AddressValueError, NetmaskValueError):
                pass



    def __str__(self):
        return "Ipadress: %s (default:%s)" % (self.__repr__(), self._val)

    def __repr__(self):
        return "{}".format(self._val)

class IPAddress(TypeBaseObjFactory):
    """
    """
    NAME =  'ipaddr'

    def __init__(self):
        TypeBaseObjClassFactory.__init__(self)

    def clean(self, val="192.168.1.1"):
        if isinstance(val,IPAddressObject):
            return val
        return IPAddressObject(val)

    def check(self, ip):
        """Validates IP addresses.
        """
        return self.is_valid_ipv4(ip) or self.is_valid_ipv6(ip)

    # def clean(self, ip):
    #     ip = j.data.types.string.clean(ip)
    #     if not self.check(ip):
    #         raise ValueError("Invalid IPAddress :%s" % ip)
    #     ip_value = IPv4Address(ip)
    #     ip = ip_value.compressed
    #     return ip

    def is_valid_ipv4(self, ip):
        """ Validates IPv4 addresses.
            https: // stackoverflow.com/questions/319279/
            the use of regular expressions is INSANE. and also wrong.
            use standard python3 ipaddress module instead.
        """
        try:
            return IPv4Address(ip) and True
        except (AddressValueError, NetmaskValueError):
            return False

    def is_valid_ipv6(self, ip):
        """ Validates IPv6 addresses.
            https: // stackoverflow.com/questions/319279/
            the use of regular expressions is INSANE. and also wrong.
            use standard python3 ipaddress module instead.
        """
        try:
            return IPv6Address(ip) and True
        except (AddressValueError, NetmaskValueError):
            return False

    def capnp_schema_get(self, name, nr):

        return "%s @%s :Data;" % (name, nr)
