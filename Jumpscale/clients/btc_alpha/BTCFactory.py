from Jumpscale import j

JSConfigFactory = j.application.JSFactoryBaseClass

from .BTCClient import BTCClient

class GitHubFactory(JSConfigFactory):

    __jslocation__ = "j.clients.btc_alpha"
    def __init__(self):
        JSConfigFactory.__init__(self, BTCClient)
