from Jumpscale import j
from .Rogerthat import Rogerthat

JSConfigs = j.application.JSBaseConfigsClass


class RogerthatFactory(JSConfigs):
    __jslocation__ = "j.clients.rogerthat"
    _CHILDCLASS = Rogerthat
