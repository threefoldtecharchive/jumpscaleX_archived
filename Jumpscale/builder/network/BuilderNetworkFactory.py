from Jumpscale import j


class BuilderNetworkFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.network"

    def _init(self):

        self._zerotier = None
        self._coredns = None

    @property
    def zerotier(self):
        if self._zerotier is None:
            from .BuilderZerotier import BuilderZerotier
            self._zerotier = BuilderZerotier()
        return self._zerotier

    @property
    def coredns(self):
        if self._coredns is None:
            from .BuilderCoreDns import BuilderCoreDns
            self._coredns = BuilderCoreDns()
        return self._coredns
