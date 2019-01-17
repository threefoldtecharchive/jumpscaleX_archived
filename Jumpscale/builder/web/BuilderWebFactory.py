from Jumpscale import j

class BuilderWebFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.web"

    def _init(self):
        self._logger_enable()

        from .BuilderNGINX import BuilderNGINX
        from .BuilderTraefik import BuilderTraefik
        from .BuilderOpenResty import BuilderOpenResty

        self.nginx = BuilderNGINX()
        self.openresty = BuilderOpenResty()
        self.traefik = BuilderTraefik()

        #TODO:*1
