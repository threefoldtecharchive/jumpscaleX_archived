import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaIssueComment(JSBASE):
    def __init__(
            self,
            client,
            repo,
            issue,
            user,
            id=None,
            body=None,
            issue_url=None,
            html_url=None,
            pull_request_url=None,
            created_at=None
    ):
        self.client = client
        self.repo = repo
        self.issue = issue
        self.user = user
        self.created_at=created_at
        self.body = body
        self.issue_url = issue_url
        self.html_url=html_url
        self.pull_request_url = pull_request_url
        self.id=id
        JSBASE.__init__(self)

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'created_at',
            'pull_request_url',
            'html_url',
            'body',
        ]:
            v = getattr(self, attr)
            d[attr] = v
        return d

    def _validate(self, create=False, update=False, delete=False):
        """
            Validate required attributes are set before doing any operation
        """
        errors = {}
        is_valid = True

        operation = 'create'

        if create:
            if self.id:
                is_valid = False
                errors['id'] = 'Already existing'
            else:
                if not self.body:
                    is_valid = False
                    errors['body'] = 'Missing'

        elif update:
            operation = 'update'
            if not self.id:
                is_valid = False
                errors['id'] = 'Missing'
        elif delete:
            operation = 'delete'
            if not self.id:
                is_valid = False
                errors['id'] = 'Missing'

        if is_valid:
            return True, ''

        return False, '{0} Error '.format(operation) + json.dumps(errors)

    def save(self, commit=True):
        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            return is_valid, err

        try:
            resp = self.client.api.repos.issueCreateComment(data=self.data, index=str(self.issue.id), repo=self.repo.name, owner=self.user.username)
            c = resp.json()
            for k, v in c.items():
                setattr(self, k, v)
            return True, ''
        except Exception as e:
            return False, e.response.content

    def update(self, commit=True):
        is_valid, err = self._validate(update=True)

        if not commit or not is_valid:
            return is_valid, err

        try:
            username = self.user['username'] if type(self.user) == dict else self.user.username
            repo = self.repo['name'] if type(self.repo) == dict else self.repo.name
            resp = self.client.api.repos.issueEditComment(data=self.data, id=str(self.id), repo=repo, owner=username)
            return True, ''
        except Exception as e:
            return False, e.response.content

    def delete(self, commit=True):
        is_valid, err = self._validate(delete=True)

        if not commit or not is_valid:
            return is_valid, err

        try:
            username = self.user['username'] if type(self.user) == dict else self.user.username
            repo = self.repo['name'] if type(self.repo) == dict else self.repo.name
            resp = self.client.api.repos.issueDeleteComment(id=str(self.id), repo=repo, owner=username)
            return True, ''
        except Exception as e:
            return False, e.response.content

    def __repr__(self):
        return "Comment %s" % json.dumps(self.data)

    __str__ = __repr__
