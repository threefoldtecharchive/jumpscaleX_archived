from Jumpscale import j


class BuilderAppsFactory(j.builders.system._BaseFactoryClass):

    __jslocation__ = "j.builders.storage"

    def _init(self, **kwargs):
        self._syncthing = None
        self._minio = None
        self._restic = None
        self._s3cality = None
        self._zstor = None

    @property
    def syncthing(self):
        if self._syncthing is None:
            from .BuilderSyncthing import BuilderSyncthing

            self._syncthing = BuilderSyncthing()
        return self._syncthing

    @property
    def minio(self):
        if self._minio is None:
            from .BuilderMinio import BuilderMinio

            self._minio = BuilderMinio()
        return self._minio

    @property
    def restic(self):
        if self._restic is None:
            from .BuilderRestic import BuilderRestic

            self._restic = BuilderRestic()
        return self._restic

    @property
    def s3scality(self):
        if self._s3scality is None:
            from .BuilderS3Scality import BuilderS3Scality

            self._s3cality = BuilderS3Scality()
        return self._s3cality

    @property
    def zstor(self):
        if self._zstor is None:
            from .BuilderZeroStor import BuilderZeroStor

            self._zstor = BuilderZeroStor()
        return self._zstor
