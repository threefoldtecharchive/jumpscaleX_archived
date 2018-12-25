from Jumpscale import j

class BuildDBFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.db"

    def _init(self):
        self._logger_enable()
        #TODO:
        pass


