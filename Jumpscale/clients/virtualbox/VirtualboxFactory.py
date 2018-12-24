from time import sleep

from Jumpscale import j

from .VirtualboxClient import VirtualboxClient

JSBASE = j.application.JSBaseClass

class VirtualboxFactory(j.builder._BaseClass):

    def __init__(self):
        self.__jslocation__ = "j.clients.virtualbox"
        JSBASE.__init__(self)
        self._logger_enable()
        self._client=None

    @property
    def client(self):
        if self._client==None:
            self._client = VirtualboxClient()
        return self._client

