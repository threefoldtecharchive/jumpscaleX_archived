from Jumpscale import j


class BuilderLibsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.libs"

    def _init(self):

        from .BuilderOpenSSL import BuilderOpenSSL
        from .BuilderCapnp import BuilderCapnp
        from .BuilderCmake import BuilderCmake
        from .BuilderBrotli import BuilderBrotli

        self.openssl = BuilderOpenSSL()
        self.capnp = BuilderCapnp()
        self.cmake = BuilderCmake()
        self.brotli = BuilderBrotli()
        # TODO:*1
