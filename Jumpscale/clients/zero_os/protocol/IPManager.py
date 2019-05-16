from Jumpscale import j


class IPBridgeManager:
    def __init__(self, client):
        self._client = client

    def add(self, name, hwaddr=None):
        """
        Add bridge with given name and optional hardware address

        For more advanced bridge options please check the `bridge` manager.
        :param name: bridge name
        :param hwaddr: mac address (str)
        :return:
        """
        args = {"name": name, "hwaddr": hwaddr}

        return self._client.json("ip.bridge.add", args)

    def delete(self, name):
        """
        Delete bridge with given name
        :param name: bridge name to delete
        :return:
        """
        args = {"name": name}

        return self._client.json("ip.bridge.del", args)

    def addif(self, name, inf):
        """
        Add interface to bridge
        :param name: bridge name
        :param inf: interface name to add
        :return:
        """
        args = {"name": name, "inf": inf}

        return self._client.json("ip.bridge.addif", args)

    def delif(self, name, inf):
        """
        Delete interface from bridge
        :param name: bridge name
        :param inf: interface to remove
        :return:
        """
        args = {"name": name, "inf": inf}

        return self._client.json("ip.bridge.delif", args)


class IPLinkManager:
    def __init__(self, client):
        self._client = client

    def up(self, link):
        """
        Set interface state to UP

        :param link: link/interface name
        :return:
        """
        args = {"name": link}
        return self._client.json("ip.link.up", args)

    def down(self, link):
        """
        Set link/interface state to DOWN

        :param link: link/interface name
        :return:
        """
        args = {"name": link}
        return self._client.json("ip.link.down", args)

    def name(self, link, name):
        """
        Rename link

        :param link: link to rename
        :param name: new name
        :return:
        """
        args = {"name": link, "new": name}
        return self._client.json("ip.link.name", args)

    def mtu(self, link, mtu):
        """
        Update link MTU

        :param link: link to rename
        :param mtu: mtu value
        :return:
        """
        args = {"name": link, "mtu": mtu}

        return self._client.json("ip.link.mtu", args)

    def list(self):
        return self._client.json("ip.link.list", {})


class IPAddrManager:
    def __init__(self, client):
        self._client = client

    def add(self, link, ip):
        """
        Add IP to link

        :param link: link
        :param ip: ip address to add
        :return:
        """
        args = {"name": link, "ip": ip}
        return self._client.json("ip.addr.add", args)

    def delete(self, link, ip):
        """
        Delete IP from link

        :param link: link
        :param ip: ip address to remove
        :return:
        """
        args = {"name": link, "ip": ip}
        return self._client.json("ip.addr.del", args)

    def list(self, link):
        """
        List IPs of a link

        :param link: link name
        :return:
        """
        args = {"name": link}
        return self._client.json("ip.addr.list", args)


class IPRouteManager:
    def __init__(self, client):
        self._client = client

    def add(self, dev, dst, gw=None):
        """
        Add a route

        :param dev: device name
        :param dst: destination network
        :param gw: optional gateway
        :return:
        """
        args = {"dev": dev, "dst": dst, "gw": gw}
        return self._client.json("ip.route.add", args)

    def delete(self, dev, dst, gw=None):
        """
        Delete a route

        :param dev: device name
        :param dst: destination network
        :param gw: optional gateway
        :return:
        """
        args = {"dev": dev, "dst": dst, "gw": gw}
        return self._client.json("ip.route.del", args)

    def list(self):
        return self._client.json("ip.route.list", {})


class IPBondManager:
    def __init__(self, client):
        self._client = client

    def add(self, bond, interfaces, mtu=1500):
        """
        Add a bond

        :param bond: bond name
        :param interfaces: list of slave links
        :param mtu: mtu value
        :return:
        """
        args = {"bond": bond, "interfaces": interfaces, "mtu": mtu}
        return self._client.json("ip.bond.add", args)

    def delete(self, bond):
        """
        Delete a bond

        :param bond: bond name
        :return:
        """
        args = {"bond": bond}
        return self._client.json("ip.bond.del", args)

    def list(self):
        return self._client.json("ip.bond.list", {})


class IPManager:
    def __init__(self, client):

        self._client = client
        self._bridge = IPBridgeManager(client)
        self._link = IPLinkManager(client)
        self._addr = IPAddrManager(client)
        self._route = IPRouteManager(client)
        self._bond = IPBondManager(client)

    @property
    def bond(self):
        """
        Bond manager
        :return:
        """
        return self._bond

    @property
    def bridge(self):
        """
        Bridge manager
        :return:
        """
        return self._bridge

    @property
    def link(self):
        """
        Link manager
        :return:
        """
        return self._link

    @property
    def addr(self):
        """
        Address manager
        :return:
        """
        return self._addr

    @property
    def route(self):
        """
        Route manager
        :return:
        """
        return self._route
