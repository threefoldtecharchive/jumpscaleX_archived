from Jumpscale import j

class BuilderWebFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.web"

    def _init(self):
        self._logger_enable()
        from .BuilderNGINX import BuilderNGINX
        self.nginx = BuilderNGINX()

        #TODO:*1




