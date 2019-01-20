from Jumpscale import j
from .SyncthingClient import SyncthingClient
JSConfigs = j.application.JSBaseConfigsClass


class SyncthingFactory(JSConfigs):
    __jslocation__ = "j.clients.syncthing"
    _CHILDCLASS = SyncthingClient
