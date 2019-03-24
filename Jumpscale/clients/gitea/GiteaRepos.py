from Jumpscale import j

from .GiteaRepoForNonOwner import GiteaRepoForNonOwner
from .GiteaRepoForOwner import GiteaRepoForOwner

JSBASE = j.application.JSBaseClass


class GiteaRepos(j.application.JSBaseClass):

    def __init__(self, client, user):
        JSBASE.__init__(self)
        self.user = user
        self.client = client
        self.position = 0

    def new(self, owner=True):
        if owner:
            return GiteaRepoForOwner(self.client, self.user)
        return GiteaRepoForNonOwner(self.client, self.user)

    def get(self, name, fetch=True):
        r = self.new()
        r.name = name
        if fetch:
            try:
                resp = self.user.client.api.repos.repoGet(repo=name, owner=self.user.username).json()
                for k, v in resp.items():
                    setattr(r, k, v)
            except Exception as e:
                if e.response.status_code == 404:
                    self._log_error('repo does not exist')
                else:
                    self._log_error(e.response.content)
                return
        return r

    @property
    def owned(self):
        result = []

        owner = self.user.is_current

        if owner:
            items = self.user.client.api.user.userCurrentListRepos().json()
        else:
            items = self.user.client.api.users.userListRepos(username=self.user.username).json()

        for item in items:
            repo = self.new(owner)
            for k, v in item.items():
                setattr(repo, k, v)
            result.append(repo)
        return result

    @property
    def starred(self):
        result = []

        if self.user.is_current:
            items = self.user.client.api.user.userCurrentListStarred().json()
        else:
            items = self.user.client.api.users.userListStarred(username=self.user.username).json()

        for item in items:
            if item['owner']['username'] == self.client.users.current.username:
                repo = self.new()
            else:
                repo = self.new(owner=False)
                u = self.client.users.new()
                for k, v in item['owner'].items():
                    setattr(u, k, v)
                repo.user  = u

            for k, v in item.items():
                setattr(repo, k, v)
            result.append(repo)
        return result

    @property
    def subscriptions(self):
        result = []

        if self.user.is_current:
            items = self.user.client.api.user.userCurrentListSubscriptions().json()
        else:
            items = self.user.client.api.users.userListSubscriptions(username=self.user.username).json()

        for item in items:
            if item['owner']['username'] == self.client.users.current.username:
                repo = self.new()
            else:
                repo = self.new(owner=False)
                u = self.client.users.new()
                for k, v in item['owner'].items():
                    setattr(u, k, v)
                repo.user = u
            for k, v in item.items():
                setattr(repo, k, v)
            result.append(repo)
        return result

    def migrate(
            self,
            auth_username,
            auth_password,
            clone_addr,
            repo_name,
            description='',
            mirror=True,
            private=True
    ):
        try:
            # user is not fetched
            if not self.user.id:
                self.user = self.client.users.get(username=self.user.username, fetch=True)

            d = {
                'auth_username': auth_username,
                'auth_password': auth_password,
                'clone_addr': clone_addr,
                'description': description,
                'mirror': mirror,
                'repo_name': repo_name,
                'uid': self.user.id,
                'private': private
            }

            r = self.user.client.api.repos.repoMigrate(d).json()
            repo = self.new()
            for k, v in r.items():
                setattr(repo, k, v)
            return repo
        except Exception as e:
            self._log_debug(e.response.content)

    def search(
            self,
            query,
            mode,
            page_number=1,
            page_size=150,
    ):

        return self.client.repos.search(query, mode, self.user.id, page_number, page_size, exclusive=True)

    def __next__(self):

        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            if item['owner']['username'] == self.client.users.current.username:
                repo = self.new()
            else:
                repo = self.new(owner=False)
                u = self.client.users.new()
                for k, v in item['owner'].items():
                    setattr(u, k, v)
                repo.user = u
            for k, v in item.items():
                setattr(repo, k, v)
            return repo
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        if self.user.is_current:
            self._items = self.client.api.user.userCurrentListRepos().json()
        else:
            self._items = self.client.api.users.userListRepos(username=self.user.username).json()

        return self

    def __repr__ (self):
        return "<Repos Iterator for user: {0}>".format(self.user.username)

    __str__ = __repr__
