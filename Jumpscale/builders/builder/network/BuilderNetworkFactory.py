from Jumpscale import j


class BuilderNetworkFactory(j.builders.system._BaseFactoryClass):

    __jslocation__ = "j.builders.network"

    def _init(self, **kwargs):

        self._zerotier = None
        self._coredns = None
        self._gateway = None
        self._tcprouter = None

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

    @property
    def gateway(self):
        if self._gateway is None:
            from .BuilderGateway import BuilderGateway

            self._gateway = BuilderGateway()
        return self._gateway

    @property
    def tcprouter(self):
        if self._tcprouter is None:
            from .BuilderTCPRouter import BuilderTCPRouter

            self._tcprouter = BuilderTCPRouter()
        return self._tcprouter
