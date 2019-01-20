from Jumpscale import j
from .RacktivityClient import RacktivityClient

JSConfigs = j.application.JSBaseConfigsClass


class RacktivityFactory(JSConfigs):
    __jslocation__ = "j.clients.racktivity"
    _CHILDCLASS = RacktivityClient
