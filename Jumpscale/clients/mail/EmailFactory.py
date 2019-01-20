from .EmailClient import EmailClient
from Jumpscale import j
JSConfigs = j.application.JSBaseConfigsClass


class EmailFactory(JSConfigs):
    __jslocation__ = "j.clients.email"
    _CHILDCLASS = EmailClient
