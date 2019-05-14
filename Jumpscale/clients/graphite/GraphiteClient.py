from Jumpscale import j

import socket
import time

try:
    import urllib.request
    import urllib.parse
    import urllib.error
except BaseException:
    import urllib.parse as urllib

JSConfigClient = j.application.JSBaseConfigClass


class GraphiteClient(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.graphite.client
        name* = "" (S)
        server = "127.0.0.1" (ipaddr)
        carbon_port = 2003 (ipport)
        graphite_port = 8081 (ipport)
        """

    def _init(self):
        self._SERVER = self.server
        self._CARBON_PORT = self.carbon_port
        self._GRAPHITE_PORT = self.graphite_port
        self._url = "http://%s:%s/render" % (self._SERVER, self._GRAPHITE_PORT)

    def send(self, msg):
        """
        e.g. foo.bar.baz 20
        :param msg: message to be sent
        :type msg: str
        """
        out = ""
        for line in msg.split("\n"):
            out += "%s %d\n" % (line, int(time.time()))
        sock = socket.socket()
        sock.connect((self._SERVER, self._CARBON_PORT))
        sock.sendall(out)
        sock.close()

    def close(self):
        pass

    def query(self, query_=None, **kwargs):
        import requests

        query = query_.copy() if query_ else dict()
        query.update(kwargs)
        query["format"] = "json"
        if "from_" in query:
            query["from"] = query.pop("from_")
        qs = urllib.parse.urlencode(query)
        url = "%s?%s" % (self._url, qs)
        return requests.get(url).json()
