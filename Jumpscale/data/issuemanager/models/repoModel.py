from Jumpscale import j

from data.capnp.ModelBase import ModelBase


class RepoModel(ModelBase):
    """
    Model Class for a repo object
    """

    def index(self):
        self.collection.add2index(**self.to_dict())

    def gitHostRefSet(self, name, id, url):
        return j.clients.gogs._gitHostRefSet(self, name, id, url)

    def gitHostRefExists(self, name, url):
        return j.clients.gogs._gitHostRefExists(self, name, url)
