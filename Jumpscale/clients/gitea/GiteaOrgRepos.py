from Jumpscale import j

from .GiteaOrgRepo import GiteaOrgRepo

JSBASE = j.application.JSBaseClass


class GiteaOrgRepos(j.builder._BaseClass):
    def __init__(self, organization):
        JSBASE.__init__(self)
        self.organization = organization
        self.position = 0

    def get(self, org, fetch=False):
        """

        """
        o = self.new()
        if fetch:
            resp = self.client.api.orgs.orgGet(org=org).json()
            for k, v in resp.items():
                setattr(o, k, v)
        return o

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            key = GiteaOrgRepo(user=self.user)
            for k, v in item.items():
                setattr(key, k, v)
            return key
        else:
            self.position = 0
            raise StopIteration()


    def __iter__(self):
        self._items = self.user.client.api.orgs.orgListRepos().json()
        return self

    __str__ = __repr__ = lambda self: "Gitea Repos Iterator for organization: {0}".format(self.organization.username)

