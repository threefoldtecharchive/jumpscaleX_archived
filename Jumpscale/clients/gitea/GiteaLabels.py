from Jumpscale import j

from .GiteaLabel import GiteaLabel

JSBASE = j.application.JSBaseClass


class GiteaLabels(j.application.JSBaseClass):
    def __init__(self, client, repo, user, issue=None):
        JSBASE.__init__(self)
        self.client = client
        self.repo = repo
        self.user = user
        self.issue = issue
        self.position = 0

    def new(self):
        return GiteaLabel(self.client, self.repo, self.user, self.issue)

    def get(self, id, fetch=False):
        o = self.new()
        if fetch:
            resp = self.client.api.repos.issueGetLabel(id=str(id), repo=self.repo.name, owner=self.user.username).json()
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
        if not self.issue:
            items = self.client.api.repos.issueListLabels(repo=self.repo.name, owner=self.user.username).json()
        else:
            items = self.client.api.repos.issueGetLabels(index=str(self.issue.id), repo=self.repo.name, owner=self.user.username).json()
        for item in items:
            c = self.new()
            for k, v in item.items():
                setattr(c, k, v)
            self._items.append(c)
        return self

    def clear(self):
        if not self.issue:
            raise Exception('Only supported for issues, not whole repos')
        self.client.api.repos.issueClearLabels(index=str(self.issue.id), repo=self.repo.name, owner=self.user.username).json()

    __str__ = __repr__ = lambda self: "Gitea Labels Iterator for repo: {0}".format(self.repo.name)

