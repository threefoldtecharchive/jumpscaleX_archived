import json
from Jumpscale import j

from clients.gitea import GiteaRepos

JSBASE = j.application.JSBaseClass

from .GiteaTeamMembers import GiteTeamMembers

class GiteaTeam(JSBASE):
    def __init__(
            self,
            client,
            organization,
            id=None,
            description=None,
            name=None,
            permission=None
    ):
        self.client = client
        self.organization = organization
        self.description=description
        self.name = name
        self.permission = permission
        self.id=id
        JSBASE.__init__(self)

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'description',
            'name',
            'permission',
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
                if not self.name:
                    is_valid = False
                    errors['name'] = 'Missing'

            if not self.permission:
                is_valid = False
                errors['permission'] = 'Missing'

            elif not self.permission in ['owner', 'admin', 'read', 'write']:
                is_valid = False
                errors['permission'] = "Only allowed [owner, admin, read, write]"


        elif update:
            operation = 'update'
            if not self.id:
                is_valid = False
                errors['id'] = 'Missing'

            if not self.permission:
                is_valid = False
                errors['permission'] = 'Missing'

            elif not self.permission in ['owner', 'admin', 'read', 'write']:
                is_valid = False
                errors['permission'] = "Only allowed [owner, admin, read, write]"

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
            team = self.client.api.orgs.orgCreateTeam(data=self.data, org=self.organization.username).json()
            for k, v in team.items():
                setattr(self, k, v)
            return True, ''
        except Exception as e:
            return False, e.response.content

    def update(self, commit=True):
        is_valid, err = self._validate(update=True)

        if not commit or not is_valid:
            return is_valid, err
        try:
            resp = self.client.api.teams.orgEditTeam(data=self.data, id=str(self.id))
            return True, ''
        except Exception as e:
            return False, e.response.content

    def delete(self, commit=True):
        is_valid, err = self._validate(update=True)

        if not commit or not is_valid:
            return is_valid, err

        try:
            resp = self.client.api.teams.orgDeleteTeam(id=str(self.id))
            return True, ''
        except Exception as e:
            return False, e.response.content

    @property
    def members(self):
        return GiteTeamMembers(self.client, self)

    @property
    def repos(self):
        return GiteaRepos()

    def __repr__(self):
        return "<Team> %s" % json.dumps(self.data)

    __str__ = __repr__
