from Jumpscale import j
from .PacketNet import PacketNet

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class PacketNetFactory(JSConfigBaseFactory):

    __jslocation__ = "j.clients.packetnet"
    _CHILDCLASS = PacketNet

    def _init(self):
        self.connections = {}

    def test(self):
        """
        do:
        js_shell 'j.clients.packetnet.test()'
        """
        client = self.get()
        self._logger.debug(client.servers_list())

        # TODO:*1 connect to packet.net * boot zero-os
        # connect the client to zero-os
        # do a ping
