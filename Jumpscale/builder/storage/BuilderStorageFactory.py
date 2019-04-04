from Jumpscale import j

class BuilderAppsFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.storage"

    def _init(self):
        self._syncthing = None
        self._minio = None
        self._restic = None
        self._s3cality = None

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
    def s3cality(self):
        if self._s3cality is None:
            from .BuilderS3Scality import BuilderS3Scality
            self._s3cality = BuilderS3Scality()
        return self._s3cality
