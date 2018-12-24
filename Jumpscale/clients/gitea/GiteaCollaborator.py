import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaCollaborator(j.application.JSBaseClass):
    def __init__(
            self,
            client,
            repo,
            name=None,
            commit=None,
            committer=None,
            id=None,
            url=None,
            message=None,
            timestamp=None,
            verification=None
    ):
        self.client = client
        self.repo = repo
        self.name = name
        self.commit = commit
        self.committer = committer
        self.id = id
        self.message=message
        self.url = url
        self.timestamp = timestamp
        self.verification = verification

        JSBASE.__init__(self)

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'name',
            'commit',
            'committer',
            'message',
            'timestamp',
            'verification',
            'url'
        ]:
            v = getattr(self, attr)
            d[attr] = v
        return d

    def __repr__(self):
        return "Branch <%s>" % json.dumps(self.data)

    __str__ = __repr__
