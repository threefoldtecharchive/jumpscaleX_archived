from Jumpscale import j

JSConfigFactory = j.application.JSFactoryBaseClass
JSConfigClient = j.application.JSBaseClass
TEMPLATE = """
host = "localhost"
port = 27017
username = ""
password_ = ""
alias = ""
db = ""
authentication_source = ""
authentication_mechanism = ""
ssl = false # Boolean
replicaset = ""
"""

class MongoEngineClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        from mongoengine import connect
        super().__init__(instance=instance, data=data, parent=parent, template=TEMPLATE, interactive=interactive)
        kwargs = {}
        for key, value in self.config.data.items():
            if value != "":
                kwargs[key.rstrip('_')] = value
        connect(**kwargs)


class MongoClientFactory(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.mongoengine"
        self.__imports__ = "mongoengine"
        super().__init__(MongoEngineClient)
