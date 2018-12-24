from Jumpscale import j

from .GiteaRepoPullRequest import GiteaRepoPullRequest

JSBASE = j.application.JSBaseClass


class GiteaRepoPullRequests(j.builder._BaseClass):
    def __init__(self, client, repo, user):
        JSBASE.__init__(self)
        self.client = client
        self.repo = repo
        self.user = user
        self.position = 0

    def new(self):
        return GiteaRepoPullRequest(self.client, self.repo, self.user)

    def get(self, id, fetch=False):
        """

        """

        o = self.new()
        if fetch:
            resp = self.client.api.repos.repoGetPullRequest(repo=self.repo.name, owner=self.user.username, index=str(id)).json()
            for k, v in resp.items():
                setattr(o, k, v)
        o.user = self.user
        o.repo = self.repo

        return o

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            pr = GiteaRepoPullRequest(self.client, self.repo, self.user)

            for k, v in item.items():
                setattr(pr, k, v)
            return pr
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.client.api.repos.repoListPullRequests(repo=self.repo.name, owner=self.user.username).json()
        return self

    __str__ = __repr__ = lambda self: "Gitea PR Iterator for Repo: {0}".format(self.repo.name)

