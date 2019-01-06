from .ZeroHubClient import ZeroHubClient
from Jumpscale import j

JSConfigFactory = j.application.JSFactoryBaseClass


class ZeroHubFactory(JSConfigFactory):
    __jslocation__ = "j.clients.zhub"
    _CHILDCLASS = ZeroHubClient
