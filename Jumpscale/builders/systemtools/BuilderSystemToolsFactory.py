from Jumpscale import j

class BuilderSystemToolsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.systemtools"

    def _init(self):
        from .BuildersRsync import BuilderRsync
        self.rsync = BuilderRsync{}
