from Jumpscale import j
from influxdb import client as influxdb
import requests
from requests.auth import HTTPBasicAuth

JSConfigClient = j.application.JSBaseConfigClass


class InfluxClient(JSConfigClient, influxdb.InfluxDBClient):
    _SCHEMATEXT = """
        @url = jumpscale.influxdb.client
        name* = "" (S)
        host = "127.0.0.1" (ipaddr)
        port = 8086 (ipport)
        username = "root" (S)
        password = "" (S)
        database = "" (S)
        ssl = False (B)
        verify_ssl = False (B)
        timeout = 0 (I)
        use_udp = False (B)
        udp_port = 4444 (ipport)
        """

    def _init(self):
        influxdb.InfluxDBClient.__init__(
            self,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password or None,
            database=self.database or None,
            ssl=self.ssl,
            verify_ssl=self.verify_ssl,
            timeout=self.timeout or None,
            use_udp=self.use_udp,
            udp_port=self.udp_port)
