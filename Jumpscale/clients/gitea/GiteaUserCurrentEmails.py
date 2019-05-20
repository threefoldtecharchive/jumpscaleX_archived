from Jumpscale import j

from .GiteaUserCurrentEmail import GiteaUserCurrentEmail

JSBASE = j.application.JSBaseClass


class GiteaUserCurrentEmails(j.application.JSBaseClass):
    def __init__(self, client, user):
        self.user = user
        self.client = client
        self.position = 0
        self._items = []
        JSBASE.__init__(self)

    def add(self, emails):
        try:
            self.client.api.user.userAddEmail({"emails": emails})
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False

    def remove(self, emails):
        try:
            self.client.api.user.userDeleteEmail({"emails": emails})
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False

    def __next__(self):
        if self.position >= len(self._items):
            self.position = 0
            raise StopIteration()
        item = self._items[self.position]
        self.position += 1
        return item

    def __iter__(self):
        items = self.client.api.user.userListEmails().json()
        for item in items:
            email = GiteaUserCurrentEmail(self.client, self.user)
            for k, v in item.items():
                setattr(email, k, v)
            self._items.append(email)
        return self

    def __repr__(self):
        return "<Emails Iterator for user: {0}>".format(self.user.username)

    __str__ = __repr__
