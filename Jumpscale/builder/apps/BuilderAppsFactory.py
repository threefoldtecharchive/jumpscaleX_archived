from Jumpscale import j

class BuilderAppsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.apps"

    def _init(self):
        self._gitea=None

    @property
    def gitea(self):
        if self._gitea is None:
            from .BuilderGitea import BuilderGitea
            self._gitea = BuilderGitea()
        return self._gitea





