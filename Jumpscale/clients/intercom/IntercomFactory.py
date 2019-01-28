from .IntercomClient import IntercomClient
from Jumpscale import j


JSConfigs = j.application.JSBaseConfigsClass


class Intercom(JSConfigs):

    __jslocation__ = "j.clients.intercom"
    _CHILDCLASS = IntercomClient
