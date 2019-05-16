import requests
from Jumpscale import j

from .GiteaUserCurrentGpgKey import GiteaUserCurrentGpgKey
from .GiteaGpgKeys import GiteaGpgKeys

JSBASE = j.application.JSBaseClass


class GiteaUserCurrentGpgKeys(GiteaGpgKeys):
    def new(self):
        return GiteaUserCurrentGpgKey(self.client, self.user)

    def get(self, id, fetch=True):
        key = self.new()
        key.id = id
        if fetch:
            resp = self.client.api.user.userCurrentGetGPGKey(id=str(id)).json()
            for k, v in resp.items():
                setattr(key, k, v)
        key.id = id
        return key

    def __iter__(self):
        self._items = self.user.client.api.user.userCurrentListGPGKeys().json()
        return self
