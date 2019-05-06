from Jumpscale import j

class BuilderLibsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.libs"

    def _init(self):

        from .BuilderOpenSSL import BuilderOpenSSL
        from .BuilderCapnp import BuilderCapnp
        self.openssl = BuilderOpenSSL()
        self.capnp = BuilderCapnp()
        #TODO:*1




