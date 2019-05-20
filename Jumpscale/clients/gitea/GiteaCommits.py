from Jumpscale import j


from clients.gitea.GiteaCommit import GiteaCommit

JSBASE = j.application.JSBaseClass


class GiteaCommits(j.application.JSBaseClass):
    def __init__(
        self,
        client,
        repo,
        user,
        context=None,
        created_at=None,
        creator=None,
        description=None,
        id=None,
        status=None,
        target_url=None,
        updated_at=None,
        url=None,
    ):
        self.user = user
        self.client = client
        self.repo = repo
        self.context = context
        self.created_at = created_at
        self.creator = creator
        self.description = description
        self.id = id
        self.status = status
        self.target_url = target_url
        self.uodated_at = updated_at
        self.url = url

    def get(self, ref):

        result = []
        r = self.client.api.repos.repoGetCombinedStatusByRef(ref, self.repo.name, self.user.username).json()
        for item in r:
            o = GiteaCommit(self.client, self.repo, self.user)
            for k, v in item.items():
                setattr(o, k, v)
            result.append(o)
        return result

    __str__ = __repr__ = lambda self: "Commits Object for repo %s" % self.repo.name
