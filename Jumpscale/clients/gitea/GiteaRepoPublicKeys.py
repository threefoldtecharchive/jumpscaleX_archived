import requests
from Jumpscale import j

from .GiteaRepoPublicKey import GiteaRepoPublicKey

JSBASE = j.application.JSBaseClass


class GiteaRepoPublicKeys(j.application.JSBaseClass):

    def __init__(self, user, repo):
        JSBASE.__init__(self)
        self.user = user
        self.position = 0
        self.repo = repo

    def new(self):
        return GiteaRepoPublicKey(self.user, self.repo)

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            key = GiteaRepoPublicKey(user=self.user, repo=self.repo)
            for k, v in item.items():
                setattr(key, k, v)
            return key
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.user.client.api.repos.repoListKeys(repo=self.repo.name, owner=self.user.username).json()
        return self

    __str__ = __repr__ = lambda self: "PublicKeys Iterator for repo: {0}".format(self.repo.name)
