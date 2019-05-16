from Jumpscale import j
from .MongoDBClient import MongoDBClient

JSConfigs = j.application.JSBaseConfigsClass


class MongoFactory(JSConfigs):
    __jslocation__ = "j.clients.mongodb"
    _CHILDCLASS = MongoDBClient

    def _init(self):
        self.__imports__ = "pymongo"
