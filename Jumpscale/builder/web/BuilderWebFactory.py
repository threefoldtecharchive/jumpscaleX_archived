from Jumpscale import j

class BuilderWebFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.web"

    def _init(self):
        self._logger_enable()
        from .PrefabNGINX import PrefabNGINX
        self.nginx = PrefabNGINX()

        #TODO:*1




