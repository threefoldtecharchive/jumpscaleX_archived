from Jumpscale import j

import re, ipaddress
from enum import IntEnum


class ThreeBotTypesFactory(j.application.JSBaseClass):
    """
    ThreeBotTypes Factory class
    """

    def network_address_new(self, address=None, network_type=None):
        """
        Create a new NetworkAddress, either a Hostname, IPv4- or IPv6 address.
        """
        return NetworkAddress(address=address, network_type=network_type)

    def network_address_from_json(self, obj):
        """
        JSON-decode a NetworkAddress, either a Hostname, IPv4- or IPv6 address.
        """
        return NetworkAddress.from_json(obj)

    def bot_name_new(self, value=None):
        """
        Create a new BotName from a None or string value.
        """
        return BotName(value=value)

    def bot_name_from_json(self, obj):
        """
        JSON-decode a BotName.
        """
        return BotName.from_json(obj)

    def test(self):
        """
        kosmos 'j.clients.tfchain.types.threebot.test()'
        """
        import pytest

        # 3Bot network addresses...
        # > nil address
        str(self.network_address_new()) == ""
        # > hostname
        str(self.network_address_new("hello.threefold.io")) == "hello.threefold.io"
        str(
            self.network_address_new("hello.threefold.io", network_type=NetworkAddress.Type.HOSTNAME)
        ) == "hello.threefold.io"
        # > IPv4 address
        str(self.network_address_new("83.200.201.201")) == "83.200.201.201"
        str(self.network_address_new("83.200.201.201", network_type=NetworkAddress.Type.IPV4)) == "83.200.201.201"
        # > IPv6 address
        str(self.network_address_new("2001:db8:85a3::8a2e:370:7334")) == "2001:db8:85a3::8a2e:370:7334"
        str(
            self.network_address_new("2001:db8:85a3::8a2e:370:7334", network_type=NetworkAddress.Type.IPV6)
        ) == "2001:db8:85a3::8a2e:370:7334"
        # > JSON (hostname, IPv4, IPv6)
        self.network_address_from_json("hello.threefold.io").json() == "hello.threefold.io"
        self.network_address_from_json("83.200.201.201").json() == "83.200.201.201"
        self.network_address_from_json("2001:db8:85a3::8a2e:370:7334").json() == "2001:db8:85a3::8a2e:370:7334"

        # 3Bot names...
        for name in [
            "aaaaa",
            "aaaaa.bbbbb",
            "aaaaa.aaaaa",
            "aaaaa.bbbbb.ccccc.ddddd.eeeee.fffff.ggggg.hhhhhh.jjjjj.kkkkkkkk",
            "threefold.token",
            "trading.botzone",
        ]:
            output = str(self.bot_name_new(value=name))
            if output != name:
                raise j.exceptions.Value("str: {} != {}".format(output, name))
            json_output = self.bot_name_from_json(name).json()
            if json_output != name:
                raise j.exceptions.Value("json: {} != {}".format(json_output, name))

        # > invalid bot names:
        for name in ["", "a", "a.b", "aaaaa.b", "a.bbbbb", "aaaaa:bbbbb"]:
            with pytest.raises(ValueError):
                self.bot_name_new(value=name)


from .BaseDataType import BaseDataTypeClass


class NetworkAddress(BaseDataTypeClass):
    class Type(IntEnum):
        HOSTNAME = 0
        IPV4 = 1
        IPV6 = 2

    HOSTNAME_REGEXP = re.compile(
        r"^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\.[a-zA-Z]{2,3})$"
    )
    HOSTNAME_LENGTH_MAX = 63

    def __init__(self, address=None, network_type=None):
        """
        Initialize a new NetworkAddress,
        created using a valid network type and address,
        """
        self._type = None
        self._address = None
        self.value = address
        # if network type is defined, validate it now
        if network_type is not None:
            if not isinstance(network_type, NetworkAddress.Type):
                raise j.exceptions.Value(
                    "network type is to be of type NetworkAddress.Type, not {}".format(type(network_type))
                )
            if self._type != network_type:
                raise j.exceptions.Value(
                    "network type is expected to equal {}, not {}".format(network_type, self._type)
                )

    @classmethod
    def from_json(cls, obj):
        if obj is not None and not isinstance(obj, str):
            raise j.exceptions.Value(
                "network address is expected to be an encoded string when part of a JSON object, not {}".format(
                    type(obj)
                )
            )
        if obj == "":
            obj = None
        return cls(address=obj)

    @property
    def value(self):
        """
        The NetworkAddress as a string value.
        """
        if self._type == NetworkAddress.Type.HOSTNAME:
            return self._address.decode("utf-8")
        return str(ipaddress.ip_address(self._address))

    @value.setter
    def value(self, value):
        """
        Set the NetworkAddress either from another NetworkAddress or
        more likely a string value (representing a Hostname, IPv4- or IPv6 address).
        """
        if value is None:
            self._type = NetworkAddress.Type.HOSTNAME
            self._address = bytearray()
        elif isinstance(value, str) and NetworkAddress.HOSTNAME_REGEXP.match(value):
            addr = bytearray()
            if len(value) > NetworkAddress.HOSTNAME_LENGTH_MAX:
                raise j.exceptions.Value(
                    "the length of a hostname can maximum be {} bytes long".format(NetworkAddress.HOSTNAME_LENGTH_MAX)
                )
            addr.extend(value.encode("utf-8"))
            self._type = NetworkAddress.Type.HOSTNAME
            self._address = addr
        elif isinstance(value, (str, int)):
            # or a network address is a valid (std) IPv4/IPv6 address
            na = ipaddress.ip_address(value)
            if isinstance(na, ipaddress.IPv4Address):
                self._type = NetworkAddress.Type.IPV4
                self._address = na.packed
            elif isinstance(na, ipaddress.IPv6Address):
                if na.packed[:12] == b"\0\0\0\0\0\0\0\0\0\0\xff\xff":  # IPv6 prefix for IPv4 addresses
                    self._type = NetworkAddress.Type.IPV4
                    self._address = na.packed[12:]
                else:
                    self._type = NetworkAddress.Type.IPV6
                    self._address = na.packed
            else:
                # anything else is considered an invalid network address
                raise j.exceptions.Value("invalid network address '{}' (type: {})".format(value, type(value)))
        elif isinstance(value, NetworkAddress):
            self._address = value._address.copy()
            self._type = value._type
        else:
            raise j.exceptions.Value("network address cannot be assigned a value of type {}".format(type(value)))

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def json(self):
        return self.value

    def sia_binary_encode(self, encoder):
        """
        Sia binary encoding uses the Rivine Encoder for binary-encoding
        a network address, as it is only supported for backwards compatibility.
        """
        renc = j.data.rivine.encoder_rivine_get()
        self.rivine_binary_encode_data(renc)
        encoder.add_array(renc.data)

    def rivine_binary_encode(self, encoder):
        """
        Rivine binary encoding binary-encodes the network address in an efficient way,
        where the type of the network address is encoded with a single byte prefix,
        of which in the two least significant bits are used for the type and the other 6 used for the length 'n'.
        The next 'n' bytes are used for the actual address data in raw binary format.
        """
        encoder.add_int8(self._type | (len(self._address) << 2))
        encoder.add_array(self._address)


class BotName(BaseDataTypeClass):
    REGEXP = re.compile(
        r"^[A-Za-z]{1}[A-Za-z\-0-9]{3,61}[A-Za-z0-9]{1}(\.[A-Za-z]{1}[A-Za-z\-0-9]{3,55}[A-Za-z0-9]{1})*$"
    )
    LENGTH_MAX = 63

    def __init__(self, value=None):
        """
        Initialize a new BotName.
        """
        self._value = None
        self.value = value

    @classmethod
    def from_json(cls, obj):
        if obj is not None and not isinstance(obj, str):
            raise j.exceptions.Value("bot name is expected to be an encoded string when part of a JSON object")
        if obj == "":
            obj = None
        return cls(value=obj)

    @property
    def value(self):
        """
        The internal bot name value (a string).
        """
        if self._value is None:
            return ""
        return self._value

    @value.setter
    def value(self, value):
        """
        Set the internal bot name value (as None or as a string).
        """
        if value is None:
            self._value = None
        elif isinstance(value, str):
            if len(value) > BotName.LENGTH_MAX:
                raise j.exceptions.Value(
                    "the length of a botname can maximum be {} characters long".format(BotName.LENGTH_MAX)
                )
            if BotName.REGEXP.match(value) is None:
                raise j.exceptions.Value("bot name '{}' is not valid".format(value))
            self._value = value
        elif isinstance(value, BotName):
            self._value = value._value.copy()
        else:
            raise j.exceptions.Value("bot name cannot be assigned a value of type {}".format(type(value)))

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def json(self):
        return self.value

    def sia_binary_encode(self, encoder):
        """
        Sia binary encodes a botname as a slice.
        """
        encoder.add_slice(self.value)

    def rivine_binary_encode(self, encoder):
        """
        Rivine binary encodes a botname as a slice.
        """
        encoder.add_slice(self.value)
