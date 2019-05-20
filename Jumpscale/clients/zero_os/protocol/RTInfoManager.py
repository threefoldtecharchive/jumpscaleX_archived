from . import typchk


class RTInfoManager:
    _rtinfo_start_params_chk = typchk.Checker({"host": str, "port": int, "disks": [str]})

    _rtinfo_stop_params_chk = typchk.Checker({"host": str, "port": int})

    def __init__(self, client):
        self._client = client

    def start(self, host="localhost", port=8999, disks=None):
        """
        Start rtinfo-client
        :param host: str rtinfod host address
        :param port: int rtinfod client port
        :param disks: list of prefixes of wathable disks (e.g ["sd"])

        """
        disks = [] if disks is None else disks

        args = {"host": host, "port": port, "disks": disks}
        self._rtinfo_start_params_chk.check(args)

        return self._client.json("rtinfo.start", args)

    def stop(self, host, port):
        """
        Stop rtinfo-client
        :param host: str rtinfod host address
        :param port: int rtinfod client port
        """

        args = {"host": host, "port": port}
        self._rtinfo_stop_params_chk.check(args)

        return self._client.json("rtinfo.stop", args)

    def list(self):
        """
        List running rtinfo clients
        """
        return self._client.json("rtinfo.list", {})
