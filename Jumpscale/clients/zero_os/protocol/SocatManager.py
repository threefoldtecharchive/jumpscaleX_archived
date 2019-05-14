import json

from . import typchk


class SocatManager:
    _reserve_chk = typchk.Checker({"number": int})

    def __init__(self, client):
        self._client = client

    def list(self):
        """
        List port forwards
        """
        return self._client.json("socat.list", {})

    def reserve(self, number=1):
        """
        Resever the given number of ports, and return the reserved ports

        :note: A reserved port is not granteed to be used by u only, it means
        other call to reserve for the next 2 minutes is granteed to not return
        this port.

        So to make reservation works properly, u first do `reserve` then use
        the returned port for your forwards (u have 2 minutes). Once the port
        forward is done, the port is never returned by reseve. If no port forward
        was created using this port, the port is returned to the free pool

        :note: port forward creation (using container, or kvm) doesn't check if the
        port is reserved at all.

        :param number: number of ports to reserve
        """

        args = {"number": number}

        self._reserve_chk.check(args)

        return self._client.json("socat.reserve", args)
