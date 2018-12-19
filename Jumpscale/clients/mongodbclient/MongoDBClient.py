from Jumpscale import j

from pymongo import MongoClient, MongoReplicaSetClient

JSConfigFactory = j.application.JSFactoryBaseClass
JSConfigClient = j.application.JSBaseClass
TEMPLATE = """
host = "localhost"
port = 27017
ssl = false # Boolean
replicaset = ""
"""

class MongoDBClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        c = self.config.data
        host = c['host']
        port = c['port']
        ssl = True if c['ssl'] else False
        replicaset = c['replicaset']
        self.client = None
        if replicaset == "":
            self.client = MongoClient(host=host, port=port, ssl=ssl)
        else:
            self.client = MongoReplicaSetClient(host, port=port, ssl=ssl, replicaSet=replicaset)


class MongoClientFactory(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.mongodb"
        self.__imports__ = "pymongo"
        JSConfigFactory.__init__(self, MongoDBClient)
