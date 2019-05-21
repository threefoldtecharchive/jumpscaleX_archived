from Jumpscale import j


class BuilderAppsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.virtualization"

    def _init(self):
        self._docker = None

    @property
    def docker(self):
        if self._docker is None:
            from .BuilderDocker import BuilderDocker

            self._docker = BuilderDocker()
        return self._docker