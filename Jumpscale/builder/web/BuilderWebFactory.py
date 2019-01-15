from Jumpscale import j

class BuilderWebFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.web"

    def _init(self):
        self._logger_enable()

        from .BuilderNGINX import BuilderNGINX
        from .BuilderTraefik import BuilderTraefik
        from .PrefabOpenResty import PrefabOpenResty
        from .BuilderCaddy import BuilderCaddy

        self.nginx = BuilderNGINX()
        self.openresty = PrefabOpenResty()
        self.traefik = BuilderTraefik()
        self.caddy = BuilderCaddy()

        #TODO:*1
