from Jumpscale import j
from .MongoDBClient import MongoDBClient

JSConfigs = j.application.JSBaseConfigsClass


class MongoFactory(JSConfigs):
    __jslocation__ = "j.clients.mongodb"
    _CHILDCLASS = MongoDBClient

    def _init(self):
        self.__imports__ = "pymongo"

    def start(self):
        j.builders.db.mongodb.start()

    def stop(self):
        j.builders.db.mongodb.stop()

    def test(self):
        # check README
        self.start()
        mcl = j.clients.mongodb.get("new_client", host="localhost", port=27017, ssl=False, replicaset="")

        mongo_client = mcl.client
        db = mongo_client.test_database
        collection = db.test_collection
        test_doc = {"name": "xyz", "age": "20", "hobbies": ["football", "reading", "games"]}

        clients = db.clients
        client_id = clients.insert_one(test_doc).inserted_id
        assert db.list_collection_names() == ["clients"]
        assert clients.find_one({"name": "xyz"})["name"] == "xyz"
        self.stop()
        print("TEST OK")
