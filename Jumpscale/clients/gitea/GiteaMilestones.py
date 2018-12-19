from Jumpscale import j

from .GiteaMilestone import GiteaMilestone

JSBASE = j.application.JSBaseClass


class GiteaMilestones(JSBASE):
    def __init__(self, client, repo, user):
        JSBASE.__init__(self)
        self.client = client
        self.repo = repo
        self.user = user
        self.position = 0

    def new(self):
        return GiteaMilestone(self.client, self.repo, self.user)

    def get(self, id, fetch=False):
        o = self.new()
        if fetch:
            resp = self.client.api.repos.issueGetMilestone(id=str(id), repo=self.repo.name, owner=self.user.username).json()
            for k, v in resp.items():
                setattr(o, k, v)
        return o

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            return item
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = []
        items = self.client.api.repos.issueGetMilestones(repo=self.repo.name, owner=self.user.username).json()
        for item in items:
            c = self.new()
            for k, v in item.items():
                setattr(c, k, v)
            self._items.append(c)
        return self

    __str__ = __repr__ = lambda self: "Gitea Milestones Iterator for repo: {0}".format(self.repo.name)

