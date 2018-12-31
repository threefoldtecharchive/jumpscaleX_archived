from Jumpscale import j
import requests
from requests.auth import HTTPBasicAuth


class GrafanaClient(j.application.JSBaseClass):

    _SCHEMATEXT = """
        @url = jumpscale.clients.grafana.1
        name* = "" (S)
        url* = "" (S)
        username = "" (S)
        password = "" (S)
        verify_ssl = False (B)
        """

    def _init(self):
        self._httpclient = None

    def _data_trigger_new(self):
        pass

        self.name

    def ping(self):
        pass

    def test(self):
        pass

        # IMPLEMENT some basic test using the client


# remark: can use the self.caching framework where relevant, this to speed up remote operations
