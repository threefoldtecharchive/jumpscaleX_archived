import os

from Jumpscale import j

from .ZerobootClient import zero_bootClient
JSConfigFactoryBase = j.application.JSFactoryBaseClass


class ZerobootFactory(JSConfigFactoryBase):

    def __init__(self):
        self.__jslocation__ = "j.clients.zboot"
        JSConfigFactoryBase.__init__(self, zero_bootClient)
