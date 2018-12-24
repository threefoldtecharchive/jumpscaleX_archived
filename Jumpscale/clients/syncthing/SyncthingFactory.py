from Jumpscale import j
from .SyncthingClient import SyncthingClient
JSConfigFactory = j.application.JSFactoryBaseClass


class SyncthingFactory(JSConfigFactory):
    __jslocation__ = "j.clients.syncthing"
    _CHILDCLASS = SyncthingClient
