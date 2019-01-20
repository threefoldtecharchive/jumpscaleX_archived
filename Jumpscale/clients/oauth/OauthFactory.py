import os
from Jumpscale import j
from .OauthInstance import OauthClient

JSConfigs = j.application.JSBaseConfigsClass


class OauthFactory(JSConfigs):
    __jslocation__ = "j.clients.oauth"
    _CHILDCLASS = OauthClient
