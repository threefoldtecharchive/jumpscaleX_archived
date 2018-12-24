from Jumpscale import j

from .GiteaBranch import GiteaBranch

JSBASE = j.application.JSBaseClass


class GiteaBranches(j.application.JSBaseClass):
    def __init__(self, client, repo, user):
        JSBASE.__init__(self)
        self.repo = repo
        self.client = client
        self.user = user
        self.position = 0

    def new(self):
        return GiteaBranch(repo=self.repo, client=self.client)

    def get(self, name, fetch=False):
        """

        """
        o = self.new()
        if fetch:
            resp = self.client.api.repos.repoGetBranch(repo=self.repo.name, owner=self.user.username, branch=name).json()
            for k, v in resp.items():
                setattr(o, k, v)
        return o

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            branch = GiteaBranch(client=self.client, repo=self.repo)
            for k, v in item.items():
                setattr(branch, k, v)
            return branch
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.client.api.repos.repoListBranches(repo=self.repo.name, owner=self.user.username).json()
        return self

    __str__ = __repr__ = lambda self: "Gitea Branch Iterator for Repo: {0}".format(self.repo.name)

