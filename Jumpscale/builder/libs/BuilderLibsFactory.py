from Jumpscale import j


class BuilderLibsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.libs"

    def _init(self):

        from .BuilderOpenSSL import BuilderOpenSSL
        from .BuilderCapnp import BuilderCapnp
        from .BuilderCmake import BuilderCmake

        self.openssl = BuilderOpenSSL()
        self.capnp = BuilderCapnp()
        self.cmake = BuilderCmake()
        # TODO:*1
