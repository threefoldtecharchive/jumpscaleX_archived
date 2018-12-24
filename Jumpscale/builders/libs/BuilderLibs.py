from Jumpscale import j

JSBASE = j.builder.system._BaseClass




class BuilderLibs(j.builder.system._BaseClass):

    __jslocation__ = "j.builder.libs"

    def _init(self):
        self._logger_enable()
        from .BuilderOpenSSL import BuilderOpenSSL
        self.openssl = BuilderOpenSSL()
        from .BuilderCapnp import BuilderCapnp
        self.capnp = BuilderCapnp()




