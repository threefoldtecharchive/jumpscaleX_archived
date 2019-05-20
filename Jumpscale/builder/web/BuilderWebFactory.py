from Jumpscale import j


class BuilderWebFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.web"

    def _init(self):

        from .BuilderNGINX import BuilderNGINX
        from .BuilderTraefik import BuilderTraefik
        from .BuilderOpenResty import BuilderOpenResty
        from .BuilderCaddy import BuilderCaddy
        from .BuilderCaddyFilemanager import BuilderCaddyFilemanager
        from .BuilderLapis import BuilderLapis

        self.nginx = BuilderNGINX()
        self.openresty = BuilderOpenResty()
        self.traefik = BuilderTraefik()
        self.caddy = BuilderCaddy()
        self.filemanager = BuilderCaddyFilemanager()
        self.lapis = BuilderLapis()

        # TODO:*1
