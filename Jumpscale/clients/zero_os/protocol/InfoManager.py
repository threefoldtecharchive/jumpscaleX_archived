from Jumpscale import j


class InfoManager:
    def __init__(self, client):
        self._client = client

    def cpu(self):
        """
        CPU information
        :return:
        """
        return self._client.json("info.cpu", {})

    def nic(self):
        """
        Return (physical) network devices information including IPs
        :return:
        """
        return self._client.json("info.nic", {})

    def mem(self):
        """
        Memory information
        :return:
        """
        return self._client.json("info.mem", {})

    def disk(self):
        """
        Disk information
        :return:
        """
        return self._client.json("info.disk", {})

    def os(self):
        """
        Operating system info
        :return:
        """
        return self._client.json("info.os", {})

    def port(self):
        """
        Return information about open ports on the system (similar to netstat)
        :return:
        """
        return self._client.json("info.port", {})

    def version(self):
        """
        Return OS version
        :return:
        """
        return self._client.json("info.version", {})

    def dmi(self, *types):
        """
        Get dmi output
        :return: dict
        """

        return self._client.json("info.dmi", {"types": types})
