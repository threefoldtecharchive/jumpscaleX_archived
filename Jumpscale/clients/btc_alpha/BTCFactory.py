from Jumpscale import j

JSConfigs = j.application.JSBaseConfigsClass

from .BTCClient import BTCClient


class GitHubFactory(JSConfigs):

    __jslocation__ = "j.clients.btc_alpha"
    _CHILDCLASS = BTCClient
