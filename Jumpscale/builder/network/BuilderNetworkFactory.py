from Jumpscale import j

class BuilderNetworkFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.network"

    def _init(self):
        self._logger_enable()
        from .BuilderZerotier import BuilderZerotier
        self.zerotier = BuilderZerotier()

        #TODO:*1




