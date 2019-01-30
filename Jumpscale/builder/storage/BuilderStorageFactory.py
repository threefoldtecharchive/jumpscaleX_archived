from Jumpscale import j

class BuilderAppsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.storage"

    def _init(self):
        self._syncthing = None

    @property
    def syncthing(self):
        if self._syncthing is None:
            from .BuilderSyncthing import BuilderSyncthing
            self._syncthing = BuilderSyncthing()
        return self._syncthing
