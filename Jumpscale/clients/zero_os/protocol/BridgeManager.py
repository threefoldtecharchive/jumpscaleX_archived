import json

from Jumpscale import j

from . import typchk


class BridgeManager:
    _bridge_create_chk = typchk.Checker(
        {
            "name": str,
            "hwaddr": typchk.Or(str, typchk.IsNone()),
            "network": {
                "mode": typchk.Or(typchk.Enum("static", "dnsmasq"), typchk.IsNone()),
                "nat": bool,
                "settings": typchk.Map(str, str),
            },
        }
    )

    _bridge_chk = typchk.Checker({"name": str})

    _nic_add_chk = typchk.Checker({"name": str, "nic": str})

    _nic_remove_chk = typchk.Checker({"nic": str})

    def __init__(self, client):
        self._client = client

    def create(self, name, hwaddr=None, network=None, nat=False, settings={}):
        """
        Create a bridge with the given name, hwaddr and networking setup
        :param name: name of the bridge (must be unique), 15 characters or less, and not equal to "default".
        :param hwaddr: MAC address of the bridge. If none, a one will be created for u
        :param network: Networking mode, options are none, static, and dnsmasq
        :param nat: If true, SNAT will be enabled on this bridge. (IF and ONLY IF an IP is set on the bridge
                    via the settings, otherwise flag will be ignored) (the cidr attribute of either static, or dnsmasq modes)
        :param settings: Networking setting, depending on the selected mode.
                        none:
                            no settings, bridge won't get any ip settings
                        static:
                            settings={'cidr': 'ip/net'}
                            bridge will get assigned the given IP address
                        dnsmasq:
                            settings={'cidr': 'ip/net', 'start': 'ip', 'end': 'ip'}
                            bridge will get assigned the ip in cidr
                            and each running container that is attached to this IP will get
                            IP from the start/end range. Netmask of the range is the netmask
                            part of the provided cidr.
                            if nat is true, SNAT rules will be automatically added in the firewall.
        """
        args = {"name": name, "hwaddr": hwaddr, "network": {"mode": network, "nat": nat, "settings": settings}}

        self._bridge_create_chk.check(args)

        return self._client.json("bridge.create", args)

    def list(self):
        """
        List all available bridges
        :return: list of bridge names
        """
        return self._client.json("bridge.list", {})

    def delete(self, bridge):
        """
        Delete a bridge by name

        :param bridge: bridge name
        :return:
        """
        args = {"name": bridge}

        self._bridge_chk.check(args)

        return self._client.json("bridge.delete", args)

    def nic_add(self, bridge, nic):
        """
        Attach a nic to a bridge

        :param bridge: bridge name
        :param nic: nic name
        """

        args = {"name": bridge, "nic": nic}

        self._nic_add_chk.check(args)

        return self._client.json("bridge.nic-add", args)

    def nic_remove(self, nic):
        """
        Detach a nic from a bridge

        :param nic: nic name to detach
        """

        args = {"nic": nic}

        self._nic_remove_chk.check(args)

        return self._client.json("bridge.nic-remove", args)

    def nic_list(self, bridge):
        """
        List nics attached to bridge

        :param bridge: bridge name
        """

        args = {"name": bridge}

        self._bridge_chk.check(args)

        return self._client.json("bridge.nic-list", args)
