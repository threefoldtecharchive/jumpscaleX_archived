from Jumpscale import j
from Jumpscale.sal_zos.node.Node import Node


class ZeroOSClient(j.application.JSBaseConfigClass, Node):

    _SCHEMATEXT = """
    @url = jumpscale.zos.client.1
    name* = "" (S)
    host = "127.0.0.1" (S)
    port = 6379 (ipport)
    unixsocket = "" (S)
    password = ""  (S)
    db = 0 (I)
    ssl = true (B)
    timeout = 120 (I)
    """

    def _init(self):
        client = j.clients.zos_protocol.new(**self.data._ddict)
        Node.__init__(self, client=client)

    def _update_trigger(self, key, value):
        try:
            data = {}
            data.update(self.data._ddict)
            data[key] = value
            self.client.data._data_update(data=data)
        except AttributeError:
            # not yet initializaed
            pass
