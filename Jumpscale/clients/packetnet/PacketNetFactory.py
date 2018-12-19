from Jumpscale import j


class PacketNetFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.clients.packetnet"

    def _init(self):
        self.connections = {}
        JSConfigFactory.__init__(self, PacketNet)

    def get(self,name="test"):
        pass #TODO: implement getter


    def test(self):
        """
        do:
        js_shell 'j.clients.packetnet.test()'
        """
        client = self.get()
        self._logger.debug(client.servers_list())

        #TODO:*1 connect to packet.net * boot zero-os
        #connect the client to zero-os
        #do a ping


