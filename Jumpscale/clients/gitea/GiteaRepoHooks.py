from Jumpscale import j

from .GiteaRepoHook import GiteaRepoHook

JSBASE = j.application.JSBaseClass


class GiteaRepoHooks(j.application.JSBaseClass):
    def __init__(self, client, repo, user):
        JSBASE.__init__(self)
        self.client = client
        self.repo = repo
        self.user = user
        self.position = 0

    def new(self):
        return GiteaRepoHook(self.client, self.repo, self.user)

    def get(self, id, fetch=False):
        """

        """
        o = self.new()
        if fetch:
            resp = self.client.api.repos.repoGetHook(repo=self.repo.name, id=str(id), owner=self.user.username).json()
            config = resp.pop('config')
            for k, v in resp.items():
                setattr(o, k, v)
            o.url = config['url']
            o.content_type = config['content_type']
        return o

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            hook = GiteaRepoHook(client=self.client, repo=self.repo, user=self.user)
            config = item.pop('config')
            for k, v in item.items():
                setattr(hook, k, v)
            hook.url = config['url']
            hook.content_type = config['content_type']
            return hook
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.client.api.repos.repoListHooks(repo=self.repo.name, owner=self.user.username).json()
        return self

    __str__ = __repr__ = lambda self: "Gitea Hooks Iterator for Repo: {0}".format(self.repo.name)

