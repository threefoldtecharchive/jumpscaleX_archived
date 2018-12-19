
from Jumpscale import j

import socket
import time
# import urllib.request, urllib.parse, urllib.error

try:
    import urllib.request
    import urllib.parse
    import urllib.error
except BaseException:
    import urllib.parse as urllib

JSConfigFactory = j.application.JSFactoryBaseClass
JSConfigClient = j.application.JSBaseClass
TEMPLATE = """
server = "127.0.0.1"
carbon_port = 2003
graphite_port = 8081
"""


class GraphiteFactory(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.graphite"
        JSConfigFactory.__init__(self, GraphiteClient)

class GraphiteClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        c = self.config.data
        self._SERVER = c['server']
        self._CARBON_PORT = c['carbon_port']
        self._GRAPHITE_PORT = c['graphite_port']
        self._url = "http://%s:%s/render" % (self._SERVER, self._GRAPHITE_PORT)

        # self.sock.connect((self.CARBON_SERVER, self.CARBON_PORT))

    def send(self, msg):
        """
        e.g. foo.bar.baz 20
        """
        out = ""
        for line in msg.split("\n"):
            out += '%s %d\n' % (line, int(time.time()))
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
        query['format'] = 'json'
        if 'from_' in query:
            query['from'] = query.pop('from_')
        qs = urllib.parse.urlencode(query)
        url = "%s?%s" % (self._url, qs)
        return requests.get(url).json()
