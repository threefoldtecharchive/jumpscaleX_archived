from Jumpscale import j

from .GiteaIssueComment import GiteaIssueComment

JSBASE = j.application.JSBaseClass


class GiteaIssueComments(j.application.JSBaseClass):
    def __init__(self, client, repo, issue, user):
        JSBASE.__init__(self)
        self.client = client
        self.repo = repo
        self.user = user
        self.issue = issue
        self.position = 0

    def new(self):
        return GiteaIssueComment(self.client, self.repo, self.issue, self.user)

    def get(self, id, fetch=False):
        o = self.new()
        if fetch:
            resp = self.client.api.repos.issueGetIssue(id=str(id), repo=self.repo.name, user=self.user.username).json()
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

    def search(self, updated_since=None):
        result = []
        items = self.client.api.repos.issueGetComments(
            str(self.issue.id), self.repo.name, self.user.username, updated_since
        ).json()
        for item in items:
            c = self.new()
            for k, v in item.items():
                setattr(c, k, v)
            result.append(c)
        return result

    def __iter__(self):
        self._items = self.search()
        return self

    __str__ = __repr__ = lambda self: "Gitea Issue comments Iterator for repo: {0}".format(self.repo.name)
