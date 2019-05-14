import json

from .GiteaUserCurrentEmails import GiteaUserCurrentEmails
from .GiteaUser import GiteaUser


class GiteaUserCurrent(GiteaUser):
    def __init__(self, client):
        super(GiteaUserCurrent, self).__init__(client)
        self.is_current = True

    def follow(self, username):
        try:

            self.client.api.user.userCurrentPutFollow(username=username, data=None)
            return True
        except Exception as e:
            if e.response.status_code == 404:
                self._log_debug("username does not exist")
            return False

    def unfollow(self, username):
        try:

            self.client.api.user.userCurrentDeleteFollow(username=username)
            return True
        except Exception as e:
            if e.response.status_code == 404:
                self._log_debug("username does not exist")
            return False

    @property
    def followers(self):
        result = []
        for follower in self.client.api.user.userCurrentListFollowers().json():
            user = self.client.users.new(username=follower["username"])
            for k, v in follower.items():
                setattr(user, k, v)
            result.append(user)
        return result

    @property
    def following(self):
        result = []
        for following in self.client.api.user.userCurrentListFollowing().json():
            user = self.client.users.new(username=following["username"])
            for k, v in following.items():
                setattr(user, k, v)
            result.append(user)
        return result

    def is_following(self, username):
        try:
            self.client.api.user.userCurrentCheckFollowing(followee=username)
            return True
        except Exception as e:
            if e.response.status_code != 404:
                self._log_debug("username does not exist")
            return False

    @property
    def emails(self):
        return GiteaUserCurrentEmails(self.client, self)

    def __str__(self):
        return "\n<Current User>\n%s" % json.dumps(self.data, indent=4)

    __repr__ = __str__
