from Jumpscale import j
from .Rogerthat import Rogerthat

JSConfigFactory = j.application.JSFactoryBaseClass


class RogerthatFactory(JSConfigFactory):
    __jslocation__ = "j.clients.rogerthat"
    _CHILDCLASS = Rogerthat
