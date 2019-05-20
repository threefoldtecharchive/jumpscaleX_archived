from Jumpscale import j
from .TFMuxClient import TFMuxClient

JSBaseClass = j.application.JSBaseClass


class TFMuxClientFactory(JSBaseClass):
    def __init__(self):
        __jslocation__ = "j.clients.tfmux"
        JSBaseClass.__init__(self)

    def get(self, address, port):
        return TFMuxClient(address, port)
