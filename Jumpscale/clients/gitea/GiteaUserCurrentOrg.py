import json
from Jumpscale import j

from .GiteaTeams import GiteaTeams
from .GiteaOrgMembers import GiteaOrgMembers
from .GiteaOrgRepos import GiteaOrgRepos
from .GiteaOrgHooks import GiteaOrgHooks

JSBASE = j.application.JSBaseClass


class GiteaUserCurrentOrg(j.application.JSBaseClass):

    def __init__(
            self,
            client,
            user,
            avatar_url=None,
            description=None,
            full_name=None,
            id=None,
            location=None,
            username=None,
            website=None
    ):
        JSBASE.__init__(self)
        self.client = client
        self.user = user
        self.avatar_url = avatar_url
        self.description = description
        self.full_name = full_name
        self.id = id
        self.location = location
        self.username = username
        self.website = website

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'avatar_url',
            'description',
            'full_name',
            'location',
            'username',
            'website',
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
                if not self.user.username:
                    is_valid = False
                    errors['user'] = {'username':'Missing'}

                if not self.full_name:
                    is_valid = False
                    errors['full_name'] = 'Missing'

                if not self.username:
                    is_valid = False
                    errors['username'] = 'Missing'
        elif update:
            operation = 'update'
            if not self.id:
                is_valid = False
                errors['id'] = 'Missing'

        if is_valid:
            return True, ''

        return False, '{0} Error '.format(operation) + json.dumps(errors)

    def save(self, commit=True):
        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            self._logger.debug(err)
            return is_valid
        try:
            resp = self.user.client.api.admin.adminCreateOrg(data=self.data, username=self.user.username)
            org = resp.json()
            for k, v in org.items():
                setattr(self, k, v)
            return True
        except Exception as e:
            self._logger.debug(e.response.content)
            return False

    def update(self, commit=True):
        is_valid, err = self._validate(update=True)

        if not commit or not is_valid:
            self._logger.debug(err)
            return is_valid
        try:
            resp = self.user.client.api.orgs.orgEdit(data=self.data, org=self.username)
            return True
        except Exception as e:
            self._logger.debug(e.response.content)
            return False

    @property
    def hooks(self):
        return GiteaOrgHooks(self.user.client, self)

    @property
    def repos(self):
        return GiteaOrgRepos()

    @property
    def members(self):
        return GiteaOrgMembers(self.user.client, self)

    @property
    def teams(self):
        return  GiteaTeams(self.user.client, self)

    __str__ = __repr__ = lambda self: json.dumps(self.data)
