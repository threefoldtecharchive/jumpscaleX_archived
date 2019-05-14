from Jumpscale import j

from .GiteaUserCurrentPublicKey import GiteaUserCurrentPublicKey
from .GiteaPublicKeys import GiteaPublicKeys


class GiteaUserCurrentPublicKeys(GiteaPublicKeys):
    def new(self):
        return GiteaUserCurrentPublicKey(self.client, self.user)

    def get(self, id, fetch=True):
        u = self.new(id=id)
        if fetch:
            resp = self.client.api.user.userCurrentGetKey(str(id)).json()
            for k, v in resp.items():
                setattr(u, k, v)
        return u

    def get(self, id, fetch=True):
        key = self.new()
        if fetch:
            resp = self.client.api.user.userCurrentGetKey(id=str(id)).json()
            for k, v in resp.items():
                setattr(key, k, v)
        key.id = id
        return key

    def __iter__(self):
        self._items = self.client.api.user.userCurrentListKeys().json()
        return self
