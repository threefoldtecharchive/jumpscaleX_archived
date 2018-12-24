import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaRepoPullRequest(j.builder._BaseClass):
    def __init__(
            self,
            client,
            repo,
            id=None,
            assignee=None,
            assignees=[],
            base=None,
            body=None,
            closed_at=None,
            comments=0,
            created_at=None,
            diff_url=None,
            due_date=None,
            head=None,
            html_url=None,
            labels=[],
            merge_base=None,
            merge_commit_sha=None,
            mergeable=False,
            merged=False,
            merged_at=None,
            merged_by=None,
            milestone=None,
            number=0,
            patch_url=None,
            state=None,
            title=None,
            updated_at=None,
            url=None,
            user=None,

    ):
        self.client = client
        self.repo = repo
        self.created_at=created_at
        self.updated_at=updated_at
        self.assignee = assignee
        self.assignees = assignees
        self.base=base
        self.url = url
        self.id=id
        self.body = body
        self.closed_at = closed_at
        self.comments = comments
        self.diff_url = diff_url
        self.due_date = due_date
        self.head = head
        self.html_url = html_url
        self.labels = labels
        self.merge_base = merge_base
        self.merge_commit_sha = merge_commit_sha
        self.mergeable = mergeable
        self.merged = merged
        self.merged_at = merged_at
        self.merged_by = merged_by
        self.milestone = milestone
        self.number = number
        self.patch_url = patch_url
        self.state = state
        self.title = title
        self.user = user
        JSBASE.__init__(self)

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'created_at',
            'updated_at',
            'comments',
            'diff_url',
            'due_date',
            'head',
            'html_url',
            'labels',
            'merge_base',
            'merge_commit_sha',
            'mergeable',
            'merged',
            'merged_at',
            'merged_by',
            'milestone',
            'number',
            'patch_url',
            'state',
            'title',
            'closed_at',
            'assignees',
            'assignee',
            'base',
            'body',
            'url'
        ]:
            v = getattr(self, attr)
            d[attr] = v
        return d


    def __repr__(self):
        return "PR %s" % json.dumps(self.data)

    def merge(self):
        try:
            resp = self.client.api.repos.repoMergePullRequest({}, str(self.id), self.repo.name, self.user.username)
            return True
        except:
            return False


    def is_merged(self):
        resp = self.client.api.repos.repoPullRequestIsMerged(str(self.id), self.repo.name, self.user.username)

    __str__ = __repr__
