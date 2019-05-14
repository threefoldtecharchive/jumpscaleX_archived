from Jumpscale import j

from .GiteaOrgHook import GiteaOrgHook

JSBASE = j.application.JSBaseClass


class GiteaOrgHooks(j.application.JSBaseClass):
    def __init__(self, client, organization):
        JSBASE.__init__(self)
        self.client = client
        self.organization = organization
        self.position = 0

    def new(self):
        return GiteaOrgHook(self.client, self.organization)

    def get(self, id, fetch=False):
        """

        """
        o = self.new()
        if fetch:
            resp = self.client.api.orgs.orgGetHook(org=self.organization.username, id=str(id)).json()
            config = resp.pop("config")
            for k, v in resp.items():
                setattr(o, k, v)
            o.url = config["url"]
            o.content_type = config["content_type"]
        return o

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            hook = GiteaOrgHook(client=self.client, organization=self.organization)
            config = item.pop("config")
            for k, v in item.items():
                setattr(hook, k, v)
            hook.url = config["url"]
            hook.content_type = config["content_type"]
            return hook
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.client.api.orgs.orgListHooks(self.organization.username).json()
        return self

    __str__ = __repr__ = lambda self: "Gitea Hooks Iterator for organization: {0}".format(self.organization.username)
