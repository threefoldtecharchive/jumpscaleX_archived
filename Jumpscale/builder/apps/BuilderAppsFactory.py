from Jumpscale import j

class BuilderAppsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.apps"

    def _init(self):
        # self._logger_enable()
        from .BuilderGitea import BuilderGitea
        self.gitea = BuilderGitea()

        #TODO:*1




