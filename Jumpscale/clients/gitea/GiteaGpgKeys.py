import requests
from Jumpscale import j

from .GiteaGpgKey import GiteaGpgKey

JSBASE = j.application.JSBaseClass


class GiteaGpgKeys(JSBASE):

    def __init__(self, client, user):
        JSBASE.__init__(self)
        self.client = client
        self.user = user
        self.position = 0

    def new(self):
        return GiteaGpgKey(self.client, self.user)

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            key = self.new()
            for k, v in item.items():
                setattr(key, k, v)
            return key
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.user.client.api.users.userListGPGKeys(username=self.user.username).json()
        return self

    def __repr__ (self):
        return "<GpgKeys Iterator for user: {0}>".format(self.user.username)

    __str__ = __repr__
