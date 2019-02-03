from Jumpscale import j

from .GiteaRepoForOwner import GiteaRepoForOwner
from .GiteaRepoForNonOwner import GiteaRepoForNonOwner

JSBASE = j.application.JSBaseClass


class GiteaReposForClient(j.application.JSBaseClass):
    def __init__(self, client, user):
        JSBASE.__init__(self)
        self.user = user
        self.client = client

    def search(
        self,
        query,
        mode,
        user_id=None,
        page_number=1,
        page_size=150,
        exclusive=False
    ):

        if page_size > 150 or page_size <= 0:
            page_size = 150

        if mode not in ["fork", "source", "mirror", "collaborative"]:
            self._log_error('Only modes allowed [fork, source, mirror, collaborative]')
            return []

        result = []
        items = self.user.client.api.repos.repoSearch(
            exclusive=exclusive,
            limit=page_size,
            mode=mode,
            page=page_number,
            q=query,
            uid=user_id,
        ).json()

        if not items['ok']:
            self._log_error('Response error')
            return []

        for item in items['data']:
            if item['owner']['username'] == self.client.users.current.username:
                repo = GiteaRepoForOwner(self.client, user=self.user)
            else:
                repo = GiteaRepoForNonOwner(self.client, user=None)
                u = self.client.users.new()
                for k, v in item['owner'].items():
                    setattr(u, k, v)
                repo.user = u

            for k, v in item.items():
                setattr(repo, k, v)
            result.append(repo)
        return result

    def get(self, id):
        try:
            resp = self.user.client.api.repositories.repoGetByID(id=str(id)).json()
            if resp['owner']['username'] == self.client.users.current.username:
                r = GiteaRepoForOwner(self.client, user=self.user)
            else:
                r = GiteaRepoForNonOwner(self.client, user=None)
                u = self.client.users.new()
                for k, v in resp['owner'].items():
                    setattr(u, k, v)
                r.user = u

            for k, v in resp.items():
                setattr(r, k, v)
            return r
        except Exception as e:
            if e.response.status_code == 404:
                self._log_error('id not found')
            else:
                self._log_error(e.response.content)

    def __repr__ (self):
        return "<General Repos finder and getter (by ID)>"
