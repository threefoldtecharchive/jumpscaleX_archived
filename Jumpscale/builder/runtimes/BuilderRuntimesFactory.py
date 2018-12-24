from Jumpscale import j

JSBASE = j.builder.system._BaseClass




class BuilderRuntimesFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.runtimes"

    def _init(self):
        self._logger_enable()
        from .BuilderPython import BuilderPython
        self.python = BuilderPython()
        from .BuilderPHP import BuilderPHP
        self.php = BuilderPHP()




