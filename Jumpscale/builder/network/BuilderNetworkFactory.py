from Jumpscale import j

class BuilderNetworkFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.network"

    def _init(self):
        self._logger_enable()
        self._zerotier = None
        
    @property
    def zerotier(self):
        if self._zerotier is None:
            from .BuilderZerotier import BuilderZerotier
            self._zerotier = BuilderZerotier()
        return self._zerotier


