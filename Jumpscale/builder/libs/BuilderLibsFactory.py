from Jumpscale import j

class BuilderLibsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.libs"

    def _init(self):
        self._logger_enable()
        from .BuilderOpenSSL import BuilderOpenSSL
        self.openssl = BuilderOpenSSL()

        #TODO:*1




