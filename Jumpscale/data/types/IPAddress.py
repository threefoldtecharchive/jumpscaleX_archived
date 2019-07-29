

# Copyright (C) 2019 :  TF TECH NV in Belgium see https://www.threefold.tech/
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.


from .PrimitiveTypes import String
from .TypeBaseClasses import *
from Jumpscale import j

from ipaddress import IPv4Address, IPv6Address
from ipaddress import AddressValueError, NetmaskValueError


class IPAddress(String):
    """
    ipaddress can be v4 or v6
    """

    NAME = "ipaddr , ipaddress"

    def __init__(self, default=None):
        self.BASETYPE = "string"
        self._default = default

    def check(self, value):
        if value in ["", None]:
            return True
        if isinstance(value, str):
            if value.lower() == "localhost":
                return True
            return self.is_valid_ipv4(value) or self.is_valid_ipv6(value)
        else:
            return False

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

    def clean(self, value):
        if value is None or value is "":
            return self.default_get()
        if not self.check(value):
            raise ValueError("invalid ip address %s" % value)
        else:
            if value.lower() == "localhost":
                value = "127.0.0.1"
            return value

    def default_get(self):
        if not self._default:
            self._default = "0.0.0.0"
        return self.fromString(self._default)

    def fromString(self, v):
        if not j.data.types.string.check(v):
            raise ValueError("Input needs to be string:%s" % v)
        if self.check(v):
            return v
        else:
            raise ValueError("%s not a valid ip'" % (v))
