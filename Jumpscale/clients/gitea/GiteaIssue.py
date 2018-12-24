import json
from Jumpscale import j

from .GiteaLabels import GiteaLabels
from .GiteaIssueComments import GiteaIssueComments

JSBASE = j.application.JSBaseClass


class GiteaIssue(j.builder._BaseClass):

    def __init__(
            self,
            client,
            user,
            repo,
            id=None,
            assignee=None,
            assignees=[],
            body=None,
            closed=False,
            due_date=None,
            labels = [],
            milestone=0,
            title=None,
            state=None,
            updated_at=None,
            url = None,
    ):
        JSBASE.__init__(self)
        self.client = client
        self.repo = repo
        self.user = user
        self.id = id
        self.assignee = assignee
        self.assignees = assignees
        self.body = body
        self.closed=closed
        self.due_date = due_date
        self.labels = labels
        self.milestone = milestone
        self.title = title
        self.state = state
        self.updated_at = updated_at
        self.url = url

    @property
    def data(self):
        d = {}
        for attr in [
            'id',
            'assignee',
            'assignees',
            'body',
            'due_date',
            'labels',
            'milestone',
            'title',
            'state',
            'url',
            'updated_at'
        ]:
            v = getattr(self, attr)
            d[attr] = v
        return d

    def _validate(self, create=False, update=False):
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

                if not self.title:
                    is_valid = False
                    errors['title'] = 'Missing'

                if not self.repo:
                    is_valid = False
                    errors['repo'] = 'Missing'

        elif update:
            operation = 'update'
            if not self.id:
                is_valid = False
                errors['id'] = 'Missing'

        if is_valid:
            return True, ''

        return False, '{0} Error '.format(operation) + json.dumps(errors)

    def save(self, commit=True):
        """
        Create public key for user
        """
        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            return is_valid, err

        try:
            resp = self.client.api.repos.issueCreateIssue(self.data, self.repo.name, self.user.username).json()

            for k, v in resp.items():
                setattr(self, k, v)

            # coming response ID is global issue id
            self.id = self.number

            return True, ''
        except Exception as e:
            return False, e.response.content

    def update(self, commit=True):
        """
        Create public key for user
        """
        is_valid, err = self._validate(update=True)

        if not commit or not is_valid:
            return is_valid, err

        repo = None
        if type(self.repo) == dict:
            repo = self.repo['name']
        else:
            repo = self.repo.name

        username = None
        if type(self.user) == dict:
            username = self.user['username']
        else:
            username = self.user.username

        try:
            resp = self.client.api.repos.issueEditIssue(self.data, str(self.id), repo, username)
            return True, ''
        except Exception as e:
            return False, e.response.content

    @property
    def issue_comments(self):
        return GiteaIssueComments(self.client, self.repo, self, self.user)


    __str__ = __repr__ = lambda self: json.dumps(self.data)
