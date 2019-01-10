from .IntercomClient import IntercomClient
from Jumpscale import j


JSConfigFactory = j.application.JSFactoryBaseClass


class Intercom(JSConfigFactory):

    __jslocation__ = "j.clients.intercom"
    _CHILDCLASS = IntercomClient
