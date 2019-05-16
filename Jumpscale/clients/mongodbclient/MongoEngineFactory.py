from Jumpscale import j
from .MongoEngineClient import MongoEngineClient

JSConfigs = j.application.JSBaseConfigsClass


class MongoEngineFactory(JSConfigs):
    __jslocation__ = "j.clients.mongoengine"
    _CHILDCLASS = MongoEngineClient

    def _init(self):
        self.__imports__ = "mongoengine"
