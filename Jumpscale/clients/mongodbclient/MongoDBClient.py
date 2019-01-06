from Jumpscale import j

from pymongo import MongoClient, MongoReplicaSetClient


JSConfigClient = j.application.JSBaseConfigClass


class MongoDBClient(JSConfigClient):
    _SCHEMATEXT = """
        @url = jumpscale.MongoDB.client
        name* = "" (S)
        host = "localhost" (S)
        port = 27017 (ipport)
        ssl = False (B)
        replicaset = "" (S)
        """

    def _init(self):
        host = self.host
        port = self.port
        ssl = True if self.ssl else False
        replicaset = self.replicaset
        self.client = None
        if replicaset == "":
            self.client = MongoClient(host=host, port=port, ssl=ssl)
        else:
            self.client = MongoReplicaSetClient(host, port=port, ssl=ssl, replicaSet=replicaset)
