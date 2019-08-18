from Jumpscale import j
from .MongoEngineClient import MongoEngineClient

JSConfigs = j.application.JSBaseConfigsClass


class MongoEngineFactory(JSConfigs):
    __jslocation__ = "j.clients.mongoengine"
    _CHILDCLASS = MongoEngineClient

    def _init(self, **kwargs):
        self.__imports__ = "mongoengine"
