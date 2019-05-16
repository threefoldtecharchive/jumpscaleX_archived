from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaCommit(j.application.JSBaseClass):
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

    __str__ = __repr__ = lambda self: "Commit Object %s for repo %s" % (self.id, self.repo.name)
