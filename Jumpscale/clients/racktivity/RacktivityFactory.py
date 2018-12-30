from Jumpscale import j
from .RacktivityClient import RacktivityClient

JSConfigFactory = j.application.JSFactoryBaseClass


class RacktivityFactory(JSConfigFactory):
    __jslocation__ = "j.clients.racktivity"
    _CHILDCLASS = RacktivityClient
