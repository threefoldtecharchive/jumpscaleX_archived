from Jumpscale import j
from .CoreXClient import CoreXClient

JSBaseClass = j.application.JSBaseClass


class CoreXClientFactory(JSBaseClass):
    def __init__(self):
        __jslocation__ = "j.clients.corex"
        JSBaseClass.__init__(self)

    def get(self, address, port):
        return CoreXClient(address, port)
