import json
from Jumpscale import j

from .GiteaUser import GiteaUser
from .GiteaUserCurrent import GiteaUserCurrent

JSBASE = j.application.JSBaseClass


class GiteaUsers(j.application.JSBaseClass):
    def __init__(self, client):
        JSBASE.__init__(self)
        self.client = client
        self._current = None

    @property
    def current(self):
        if not self._current:
            item = self.client.api.user.userGetCurrent().json()
            u = GiteaUserCurrent(self.client)
            for k, v in item.items():
                setattr(u, k, v)
            self._current = u
        return self._current

    def new(self, username=None):
        if username == self.current.username:
            return GiteaUserCurrent(client=self.client, username=username)
        return GiteaUser(client=self.client, username=username)

    def get(self, username, fetch=True):
        if username == self.current.username:
            return self.current

        u = self.new()
        u.username = username
        if fetch:
            resp = self.client.api.users.userGet(username=username).json()
            for k, v in resp.items():
                setattr(u, k, v)
        return u

    def search(self, query, limit=None):
        users = []
        resp = self.client.api.users.userSearch(limit=limit, q=query).json()
        for user in resp["data"]:
            if user["username"] == self.current.username:
                new = GiteaUserCurrent(self.client)
            else:
                new = self.new()
            for k, v in user.items():
                setattr(new, k, v)
            users.append(new)
        return users

    def is_following(self, follower, followee):
        try:
            self.client.api.users.userCheckFollowing(follower, followee)
        except Exception as e:
            if e.response.status_code == 404:
                self._log_debug("follower or followee not found")
            else:
                self._log_debug(e.response.content)
            return False
        return True

    def __repr__(self):
        return "<Users>"

    __str__ = __repr__
