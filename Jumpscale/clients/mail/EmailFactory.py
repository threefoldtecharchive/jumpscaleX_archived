from .EmailClient import EmailClient
from Jumpscale import j
JSConfigFactory = j.application.JSFactoryBaseClass


class EmailFactory(JSConfigFactory):
    __jslocation__ = "j.clients.email"
    _CHILDCLASS = EmailClient
