from Jumpscale import j


class BuilderWebFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builders.web"

    def _init(self):

        self._nginx = None
        self._openresty = None
        self._traefik = None
        self._caddy = None
        self._filemanager = None
        self._lapis = None

    @property
    def nginx(self):
        if self._nginx is None:
            from .BuilderNGINX import BuilderNGINX

            self._nginx = BuilderNGINX()
        return self._nginx

    @property
    def openresty(self):
        if self._openresty is None:
            from .BuilderOpenResty import BuilderOpenResty

            self._openresty = BuilderOpenResty()
        return self._openresty

    @property
    def traefik(self):
        if self._traefik is None:
            from .BuilderTraefik import BuilderTraefik

            self._traefik = BuilderTraefik()
        return self._traefik

    @property
    def caddy(self):
        if self._caddy is None:
            from .BuilderCaddy import BuilderCaddy

            self._caddy = BuilderCaddy()
        return self._caddy

    @property
    def filemanager(self):
        if self._filemanager is None:
            from .BuilderCaddyFilemanager import BuilderCaddyFilemanager

            self._filemanager = BuilderCaddyFilemanager()
        return self._filemanager

    @property
    def lapis(self):
        if self._lapis is None:
            from .BuilderLapis import BuilderLapis

            self._lapis = BuilderLapis()
        return self._lapis
