from Jumpscale import j

from .NBHClient import NBHClient

JSConfigBase = j.application.JSBaseConfigsClass



class NBHClientFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = "j.clients.nbhvertex"
    _CHILDCLASS = NBHClient
