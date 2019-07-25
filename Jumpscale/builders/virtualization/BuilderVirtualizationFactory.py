from Jumpscale import j


class BuilderAppsFactory(j.builders.system._BaseFactoryClass):

    __jslocation__ = "j.builders.virtualization"

    def _init(self, **kwargs):
        self._docker = None

    @property
    def docker(self):
        if self._docker is None:
            from .BuilderDocker import BuilderDocker

            self._docker = BuilderDocker()
        return self._docker
