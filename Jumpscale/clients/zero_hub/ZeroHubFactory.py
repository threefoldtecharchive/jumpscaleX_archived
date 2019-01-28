from .ZeroHubClient import ZeroHubClient
from Jumpscale import j

JSConfigs = j.application.JSBaseConfigsClass


class ZeroHubFactory(JSConfigs):
    __jslocation__ = "j.clients.zhub"
    _CHILDCLASS = ZeroHubClient
