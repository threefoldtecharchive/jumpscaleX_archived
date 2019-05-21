from Jumpscale import j

JSBASE = j.builder.system._BaseClass


class BuilderLibs(j.builder.system._BaseClass):

    __jslocation__ = "j.builder.libs"

    def _init(self):

        from .BuilderOpenSSL import BuilderOpenSSL 

        self.openssl = BuilderOpenSSL()
        from .BuilderCapnp import BuilderCapnp

        self.capnp = BuilderCapnp()
        from .BuilderLibffi import BuilderLibffi

        self.libffi = BuilderLibffi()
        from .BuilderCmake import BuilderCmake

        self.cmake = BuilderCmake()


