from Jumpscale import j


JSBASE = j.application.JSBaseClass


class GiteaCollaborators(j.application.JSBaseClass):
    def __init__(self, client, repo, user):
        JSBASE.__init__(self)
        self.repo = repo
        self.client = client
        self.user = user
        self.position = 0


    def add(self, username):
        try:
            resp = self.client.api.repos.repoAddCollaborator(repo=self.repo.name, owner=self.user.username, collaborator=username, data={})
            return True, ''
        except Exception as e:
                return False, e.response.content

    def remove(self, username):
        try:
            resp = self.client.api.repos.repoDeleteCollaborator(repo=self.repo.name, owner=self.user.username, collaborator=username)
            return True, ''
        except Exception as e:
                return False, e.response.content

    def is_collaborator(self, username):
        try:
            resp = self.client.api.repos.repoCheckCollaborator(repo=self.repo.name, owner=self.user.username, collaborator=username)
            return True
        except Exception as e:
                return False

    def __next__(self):
        from .GiteaUser import GiteaUser

        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            user = GiteaUser(client=self.client)
            for k, v in item.items():
                setattr(user, k, v)
            return user
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.client.api.repos.repoListCollaborators(repo=self.repo.name, owner=self.user.username).json()
        return self

    __str__ = __repr__ = lambda self: "Gitea Branch Iterator for Repo: {0}".format(self.repo.name)

