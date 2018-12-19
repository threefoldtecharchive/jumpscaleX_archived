"""
This modules defines types related to networks in a tfchain Tx context
"""

import re
import ipaddress
from enum import IntEnum

from JumpscaleLib.clients.blockchain.tfchain.encoding import binary

REGEXP_HOSTNAME = re.compile(r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$')
MAX_LENGTH_HOSTNAME = 63

class NetworkAddressType(IntEnum):
    HOSTNAME = 0
    IPV4 = 1
    IPV6 = 2

class NetworkAddress:
    @classmethod
    def from_string(cls, addr_str):
        if not addr_str:
            raise ValueError("nil network address")

        # a network address is either a hostname, valid if it matches our REGEXP_HOSTNAME
        if REGEXP_HOSTNAME.match(addr_str):
            addr = bytearray()
            if len(addr_str) > MAX_LENGTH_HOSTNAME:
                return ValueError("the length of a hostname can maximum be {} bytes long".format(MAX_LENGTH_HOSTNAME))
            addr.extend(addr_str.encode('utf-8'))
            return cls(network_type=NetworkAddressType.HOSTNAME, address=addr)

        # or a network address is a valid (std) IPv4/IPv6 address
        na = ipaddress.ip_address(addr_str)
        if isinstance(na, ipaddress.IPv4Address):
            return cls(network_type=NetworkAddressType.IPV4, address=na.packed)
        if isinstance(na, ipaddress.IPv6Address):
            if na.packed[:12] == b'\0\0\0\0\0\0\0\0\0\0\xff\xff': # IPv6 prefix for IPv4 addresses
                return cls(network_type=NetworkAddressType.IPV4, address=na.packed[12:])
            return cls(network_type=NetworkAddressType.IPV6, address=na.packed)

        # anything else is an invalid network address
        raise ValueError("invalid network address {}".format(addr_str))
    
    def __init__(self, network_type, address):
        """
        Initialize a new NetworkAddress
        """
        self._type = network_type
        self._address = address
    
    def __str__(self):
        if self._type == NetworkAddressType.HOSTNAME:
            return self._address.decode('utf-8')
        return str(ipaddress.ip_address(self._address))


    def __repr__(self):
        """
        Override so we have nice output in js shell if the object is not assigned
        without having to call the print method.
        """
        return str(self)


    @property
    def json(self):
        return str(self)

    @property
    def binary(self):
        bs = bytearray()
        length = len(self._address)
        bs.extend(binary.IntegerBinaryEncoder.encode(self._type|(length<<2), _kind='uint8'))
        bs.extend(self._address)
        return bs
