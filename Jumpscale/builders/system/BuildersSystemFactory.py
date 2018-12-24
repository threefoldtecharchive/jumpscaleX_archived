

from Jumpscale import j

from .BuilderBaseClass import BuilderBaseClass
from .BuilderBaseFactoryClass import BuilderBaseFactoryClass

class BuilderSystemFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.system"
    _BaseClass = BuilderBaseClass
    _BaseFactoryClass = BuilderBaseFactoryClass

    def _init(self):
        from .BuilderSystemPackage import BuilderSystemPackage
        self.package = BuilderSystemPackage()
        from .BuilderSystemPIP import BuilderSystemPIP
        self.python_pip = BuilderSystemPIP()
        from .BuilderNS import BuilderNS
        self.ns = BuilderNS()

        from .BuilderNet import BuilderNet
        self.net = BuilderNet()

        from .BuilderProcess import BuilderProcess
        self.process = BuilderProcess







