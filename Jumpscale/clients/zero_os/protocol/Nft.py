from . import typchk
from Jumpscale import j


class Nft:
    _port_chk = typchk.Checker(
        {"port": int, "interface": typchk.Or(str, typchk.IsNone()), "subnet": typchk.Or(str, typchk.IsNone())}
    )

    def __init__(self, client):
        self._client = client

    def open_port(self, port, interface=None, subnet=None):
        """
        open port
        :param port: then port number
        :param interface: an optional interface to open the port for
        :param subnet: an optional subnet to open the port for
        """
        args = {"port": port, "interface": interface, "subnet": subnet}
        self._port_chk.check(args)

        if self.rule_exists(port, interface, subnet):
            return

        return self._client.json("nft.open_port", args)

    def drop_port(self, port, interface=None, subnet=None):
        """
        close an opened port (takes the same parameters passed in open)
        :param port: then port number
        :param interface: an optional interface to close the port for
        :param subnet: an optional subnet to close the port for
        """
        args = {"port": port, "interface": interface, "subnet": subnet}
        self._port_chk.check(args)

        if not self.rule_exists(port, interface, subnet):
            return

        return self._client.json("nft.drop_port", args)

    def list(self):
        """
        List open ports
        """
        return self._client.json("nft.list", {})

    def rule_exists(self, port, interface=None, subnet=None):
        """
        Check if a rule exists (takes the same parameters passed in open)
        :param port: then port number
        :param interface: an optional interface
        :param subnet: an optional subnet
        """
        args = {"port": port, "interface": interface, "subnet": subnet}
        self._port_chk.check(args)

        return self._client.json("nft.rule_exists", args)
