import os

from Jumpscale import j

from .ZerobootClient import zero_bootClient
JSConfigFactoryBase = j.application.JSBaseConfigsClass


class ZerobootFactory(JSConfigFactoryBase):
    __jslocation__ = "j.clients.zboot"
    _CHILDCLASS = zero_bootClient
