from Jumpscale import j

class BuilderAppsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.apps"

    def _init(self):
        self._gitea = None
        self._freeflow = None
        self._digitalme = None

    @property
    def gitea(self):
        if self._gitea is None:
            from .BuilderGitea import BuilderGitea
            self._gitea = BuilderGitea()
        return self._gitea

    @property
    def freeflow(self):
        if self._freeflow is None:
            from .BuilderFreeflow import BuilderFreeflow
            self._freeflow = BuilderFreeflow()
        return self._freeflow

    @property
    def digitalme(self):
        if self._digitalme is None:
            from .BuilderDigitalME import BuilderDigitalME
            self._digitalme = BuilderDigitalME()
        return self._digitalme







