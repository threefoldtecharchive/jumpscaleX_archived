from Jumpscale import j
import requests
import time

JSConfigBase = j.application.JSBaseClass


class CoreXClient(JSConfigBase):
    _SCHEMATEXT = ""

    def __init__(self, host="localhost", port=7681):
        self.host = host
        self.port = port

    def _endpoint(self, path):
        """
        :param path:
        :return:
        """
        return "http://%s:%d/api/%s" % (self.host, self.port, path)

    def process_list(self):
        r = requests.get(self._endpoint("/processes")).json()
        return r["processes"]

    def process_clean(self):
        """
        If a process stop/die/whatever, it stay on the list to get its status
        Clean remove all non running process from the list

        :return:
        """
        r = requests.get(self._endpoint("/process/clean")).json()
        return r["status"] == "success"

    def process_start(self, args):
        """
        :param args: e.g. [‘mybib’, ‘-v’]
        :return: id of the process
        """
        if type(args) is not list:
            args = [args]

        params = {"arg[]": args}
        r = requests.get(self._endpoint("/process/start"), params=params).json()
        return r

    def process_logs(self, id):
        r = requests.get(self._endpoint("/process/logs"), params={"id": id})
        return r.text

    def process_stop(self, id):
        r = requests.get(self._endpoint("/process/stop"), params={"id": id})
        return r.json()
