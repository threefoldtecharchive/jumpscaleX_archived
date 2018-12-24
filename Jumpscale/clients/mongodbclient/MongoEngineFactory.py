from Jumpscale import j
from .MongoEngineClient import MongoEngineClient
JSConfigFactory = j.application.JSFactoryBaseClass


class MongoEngineFactory(JSConfigFactory):
    __jslocation__ = "j.clients.mongoengine"
    _CHILDCLASS = MongoEngineClient

    def _init(self):
        self.__imports__ = "mongoengine"
