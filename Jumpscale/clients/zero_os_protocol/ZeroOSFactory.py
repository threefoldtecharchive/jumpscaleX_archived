import time

from Jumpscale import j

from .Client import Client

JSConfigFactoryBase = j.application.JSFactoryBaseClass
logger = j.logger.get(__name__)


class ZeroOSFactory(JSConfigFactoryBase):
    """
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.zos_protocol"
        super().__init__(Client)
        self.connections = {}        

    def test(self):
        """
        js_shell 'j.clients.zos_protocol.test()'
        :return:
        """
        #use j.clients.zoscmd... to start a local zos
        #connect client to zos do quite some tests
        pass
