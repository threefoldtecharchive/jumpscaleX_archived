from Jumpscale import j
from mongoengine import connect
JSConfigClient = j.application.JSBaseConfigClass


class MongoEngineClient(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.MongoEngine.client
        host = "localhost" (S)
        port = 27017 (ipport)
        username = "" (S)
        password_ = "" (S)
        alias = "" (S)
        db = "" (S)
        authentication_source = "" (S)
        authentication_mechanism = "" (S)
        ssl = False (B)
        replicaset = "" (S)
        """

    def _init(self):
        kwargs = {}
        data = self.data
        for key, value in data._ddict.items():
            if value != "":
                kwargs[key.rstrip('_')] = value
        connect(**kwargs)
