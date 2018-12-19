import json

from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaIssueTime(JSBASE):
    def __init__(
            self,
            user,
            created=None,
            id=None,
            issue_id=None,
            time=0,
            user_id=0
    ):

        JSBASE.__init__(self)
        self.user = user
        self.created=created
        self.id=id
        self.issue_id=issue_id
        self.time = time
        self.user_id = user_id

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'created',
            'issue_id',
            'time',
            'user_id',
        ]:

            v = getattr(self, attr)
            if v:
                d[attr] = v
        return d

    __repr__ = __str__ = lambda self: '<Gitea Issue time> for user <%s> %s' % (self.user.username, json.dumps(self.data))




