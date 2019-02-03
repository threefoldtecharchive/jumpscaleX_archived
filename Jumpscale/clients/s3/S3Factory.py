from Jumpscale import j

from .S3Client import S3Client

JSConfigBase = j.application.JSFactoryBaseClass


class S3Factory(JSConfigBase):
    """
    """
    __jslocation__ = "j.clients.s3"
    _CHILDCLASS = S3Client

    def _init(self):
        self.__imports__ = "minio"

    def install(self):
        p = j.tools.prefab.local
        p.runtimes.pip.install("minio")


    def test(self):
        """
        do:
        js_shell 'j.clients.s3.test()'
        """

        client = self.get(name="test")
        self._log_debug(client.serversGet())
