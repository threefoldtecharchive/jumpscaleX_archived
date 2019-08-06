from . import typchk
from Jumpscale import j


class ZerotierManager:
    _network_chk = typchk.Checker({"network": str})

    def __init__(self, client):
        self._client = client

    def join(self, network):
        """
        Join a zerotier network

        :param network: network id to join
        :return:
        """
        args = {"network": network}
        self._network_chk.check(args)
        response = self._client.raw("zerotier.join", args)
        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to join zerotier network: %s" % result.stderr)

    def leave(self, network):
        """
        Leave a zerotier network

        :param network: network id to leave
        :return:
        """
        args = {"network": network}
        self._network_chk.check(args)
        response = self._client.raw("zerotier.leave", args)
        result = response.get()

        if result.state != "SUCCESS":
            raise j.exceptions.Base("failed to leave zerotier network:%s\nsterr:\n%s", (network, result.stderr))

    def list(self):
        """
        List joined zerotier networks

        :return: list of joined networks with their info
        """
        return self._client.json("zerotier.list", {})

    def info(self):
        """
        Display zerotier status info

        :return: dict of zerotier statusinfo
        """
        return self._client.json("zerotier.info", {})
