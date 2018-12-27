from Jumpscale import j

from .GiteaOrgForMember import GiteaOrgForMember
from .GiteaOrgForNonMember import GiteaOrgForNonMember


JSBASE = j.application.JSBaseClass


class GiteaOrgs(j.application.JSBaseClass):
    def __init__(self, client, user):
        JSBASE.__init__(self)
        self.user = user
        self.client = client
        self.position = 0

    def new(self):
        return GiteaOrgForMember(self.client, self.user)

    def get(self, org, fetch=True):
        if self.user.is_member_of_org(org):
            o = self.new()
        else:
            o = GiteaOrgForNonMember(self.client, self.user)

        o.username = org

        if fetch:
            resp = self.user.client.api.orgs.orgGet(org=org).json()
            for k, v in resp.items():
                setattr(o, k, v)
        return o

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            org = self.get(item['username'], fetch=False)
            for k, v in item.items():
                setattr(org, k, v)
            return org
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        if self.user.is_current:
            self._items = self.client.api.user.orgListCurrentUserOrgs().json()
        else:
            self._items = self.client.api.users.orgListUserOrgs(username=self.user.username).json()
        return self

    def __repr__ (self):
        return "<Organizations Iterator for user: {0}>".format(self.user.username)

    __str__ = __repr__
