from Jumpscale import j
from urllib.parse import urlparse
from .Client import Client


class ZeroOSFactory(j.application.JSBaseConfigsClass):
    """
    """
    _CHILDCLASS = Client
    __jslocation__ = "j.clients.zos_protocol"
