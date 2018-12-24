from Jumpscale import j
from .MongoDBClient import MongoDBClient
JSConfigFactory = j.application.JSFactoryBaseClass


class MongoFactory(JSConfigFactory):
    __jslocation__ = "j.clients.mongodb"
    _CHILDCLASS = MongoDBClient

    def __init__(self):
        self.__imports__ = "pymongo"
