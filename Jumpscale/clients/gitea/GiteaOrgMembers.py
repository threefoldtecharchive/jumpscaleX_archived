from Jumpscale import j


JSBASE = j.application.JSBaseClass


class GiteaOrgMembers(j.application.JSBaseClass):
    def __init__(self, client, organization):
        JSBASE.__init__(self)
        self.client = client
        self.organization = organization
        self.position = 0

    def get(self, id, fetch=False):
        o = self.new()
        if fetch:
            resp = self.client.api.orgs.orgListMembers(org=self.organization.username).json()
            for k, v in resp.items():
                setattr(o, k, v)
        return o

    def unregister(self, username):
        try:
            resp = self.client.api.orgs.orgDeleteMember(org=self.organization.username, username=username)
            return True, ''
        except Exception as e:
            if e.response.status_code == 404:
                return False, 'Not found'
            return False, e.response.content

    def is_member(self, username):
        try:
            resp = self.client.api.orgs.orgIsMember(org=self.organization.username, username=username).json()
            return True
        except Exception as e:
            if e.response.status_code == 404:
                return False
            raise

    def publicize(self, username):
        try:
            resp = self.client.api.orgs.orgPublicizeMember(org=self.organization.username, username=username)
            return True
        except Exception as e:
            if e.response.status_code == 404:
                return False
            raise

    def conceal(self, username):
        try:
            resp = self.client.api.orgs.orgConcealMember(org=self.organization.username, username=username)
            return True
        except Exception as e:
            if e.response.status_code == 404:
                return False
            raise

    def is_public(self, username):
        try:
            resp = self.client.api.orgs.orgIsPublicMember(org=self.organization.username, username=username).json()
            return True
        except Exception as e:
            if e.response.status_code == 404:
                return False
            raise

    @property
    def public(self):
        from .GiteaUser import GiteaUser

        result = []
        resp = self.client.api.orgs.orgListPublicMembers(org=self.organization.username).json()
        for item in resp:
            u = GiteaUser(self.client)
            for k, v in item.items():
                setattr(u, k, v)
            result.append(u)
        return result

    def __next__(self):
        from JumpScale9Lib.clients.gitea.GiteaUser import GiteaUser

        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            member = GiteaUser(client=self.client)
            for k, v in item.items():
                setattr(member, k, v)
            return member
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.client.api.orgs.orgListMembers(self.organization.username).json()
        return self

    __str__ = __repr__ = lambda self: "Gitea Members Iterator for organization: {0}".format(self.organization.username)

