import os
from Jumpscale import j
from .OauthInstance import OauthClient

JSConfigFactory = j.application.JSFactoryBaseClass


class OauthFactory(JSConfigFactory):
    __jslocation__ = "j.clients.oauth"
    _CHILDCLASS = OauthClient
