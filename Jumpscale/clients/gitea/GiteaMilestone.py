import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaMilestone(JSBASE):

    def __init__(
            self,
            client,
            repo,
            user,
            id=None,
            closed_at=None,
            closed_issues=0,
            description=None,
            due_on=None,
            open_issues=0,
            state = None,
            title=None,
    ):
        JSBASE.__init__(self)
        self.client = client
        self.repo = repo
        self.user = user
        self.id = id
        self.closed_at = closed_at
        self.closed_issues = closed_issues
        self.description = description
        self.due_on=due_on
        self.open_issues = open_issues
        self.title = title
        self.state = state

    @property
    def data(self):
        d = {}
        for attr in [
            'id',
            'closed_at',
            'closed_issues',
            'description',
            'due_on',
            'open_issues',
            'title',
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
                if not self.title:
                    is_valid = False
                    errors['title'] = 'Missing'

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
            resp = self.client.api.repos.issueCreateMilestone(data=self.data, repo=self.repo.name, owner=self.user.username)
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
            resp = self.client.api.repos.issueEditMilestone(data=self.data, id=str(self.id), repo=repo, owner=username)
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
            resp = self.client.api.repos.issueDeleteMilestone(id=str(self.id), repo=repo, owner=username)
            return True, ''
        except Exception as e:
            return False, e.response.content

    def __repr__(self):
        return "Milestone %s" % json.dumps(self.data)

    __str__ = __repr__
