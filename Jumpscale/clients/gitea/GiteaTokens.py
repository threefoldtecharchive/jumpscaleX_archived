import requests
from Jumpscale import j

from .GiteaToken import GiteaToken

JSBASE = j.application.JSBaseClass


class GiteaTokens(j.application.JSBaseClass):

    def __init__(self, client, user):
        JSBASE.__init__(self)
        self.user = user
        self.client = client
        self.position = 0

    def new(self):
        return GiteaToken(self.client, self.user)

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
        try:
            self._items = self.user.client.api.users.userGetTokens(username=self.user.username).json()
        except Exception as e:
            if e.response.status_code == 401:
                self._logger.debug('not authorized')
                self._logger.error('#FIX ME: THIS API not working')
        return self

    def __repr__ (self):
        return "<Tokens Iterator for user: {0}>".format(self.user.username)

    __str__ = __repr__
