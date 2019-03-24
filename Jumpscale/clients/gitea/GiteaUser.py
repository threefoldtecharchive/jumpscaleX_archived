import json
from Jumpscale import j

from .GiteaUserCurrentGpgKeys import GiteaUserCurrentGpgKeys
from .GiteaUserCurrentPublicKeys import GiteaUserCurrentPublicKeys
from .GiteaIssues import GiteaIssues
from .GiteaGpgKeys import GiteaGpgKeys
from .GiteaTokens import GiteaTokens
from .GiteaOrgs import  GiteaOrgs
from .GiteaRepos import  GiteaRepos
from .GiteaPublicKeys import GiteaPublicKeys

JSBASE = j.application.JSBaseClass


class GiteaUser(j.application.JSBaseClass):
    is_current = False

    def __init__(
            self,
            client,
            id=None,
            username=None,
            password=None,
            full_name=None,
            login_name=None,
            send_notify=None,
            source_id=None,
            email=None,
            active=None,
            admin=None,
            allow_git_hook=False,
            allow_import_local=False,
            location=None,
            max_repo_creation=None,
            website=None,
            avatar_url=None
    ):

        JSBASE.__init__(self)
        self.client = client
        self.id=id
        self.username=username
        self.password = password
        self.full_name = full_name
        self.login_name = login_name
        self.send_notify = send_notify
        self.source_id = source_id
        self.email = email
        self.active = active
        self.admin = admin
        self.allow_git_hook = allow_git_hook
        self.allow_import_local = allow_import_local
        self.location = location
        self.max_repo_creation = max_repo_creation
        self.website = website
        self.avatar_url = avatar_url
        self._is_admin = None

    @property
    def is_admin(self):
        if self._is_admin is None:
            try:
                self.client.api.admin.adminCreateUser(data={}).json()
            except Exception as e:
                if e.response.status_code == 403:
                    self._is_admin = False
                else:
                    # current gitea client user is admin
                    if self.client.users.current.username == self.username:
                        self._is_admin = True
                    else:
                        self._is_admin = False
        return self._is_admin

    def is_member_of_org(self, org):
        is_member = False

        if self.is_admin:
            is_member = True
        else:
            try:
                self.client.api.orgs.orgIsMember(
                    org=org,
                    username=self.username
                )
                is_member = True

            except Exception as e:
                is_member = False

        if is_member:
            self._log_debug('{0} is member of organization {1}'.format(self.username, org))
            return True
        else:
            self._log_debug('{0} is not member of organization {1}'.format(self.username, org))
            return False

    @property
    def data(self):
        """
        :return: obj as dict excluding all fields that don't have value set
        """
        d = {}

        for attr in [
            'id',
            'username',
            'password',
            'full_name',
            'login_name',
            'source_id',
            'send_notify',
            'email',
            'active',
            'admin',
            'allow_git_hook',
            'allow_import_local',
            'location',
            'max_repo_creation',
            'website',
            'avatar_url'
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
        if update:
            operation = 'update'
        elif delete:
            operation = 'delete'

        # Create or update

        if not self.is_admin:
            is_valid = False
            errors['permissions'] = 'Admin permissions required'

        if update or delete:
            if not self.username:
                is_valid = False
                errors['username'] = 'Missing'

        elif create:
            if self.id:
                errors['id'] = 'Already existing'
                is_valid = False
            else:
                if not self.password:
                    is_valid = False
                    errors['password'] = 'Missing'

                if not self.username:
                    is_valid = False
                    errors['username'] = 'Missing'

                if not self.email:
                    is_valid = False
                    errors['email'] = 'Missing'
        else:
            raise RuntimeError('You must choose operation to validate')

        if is_valid:
            return True, ''
        return False, '{0} Error '.format(operation) + json.dumps(errors)

    def save(self, commit=True):
        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            self._log_debug(err)
            return is_valid

        try:
            resp = self.client.api.admin.adminCreateUser(data=self.data)
            user = resp.json()
            for k, v in user.items():
                setattr(self, k, v)
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False

    def update(self, commit=True):
        is_valid, err = self._validate(update=True)

        if not commit or not is_valid:
            self._log_debug(err)
            return is_valid

        try:
            self.client.api.admin.adminEditUser(data=self.data, username=self.username)
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False

    def delete(self, commit=True):
        is_valid, err = self._validate(delete=True)

        if not commit or not is_valid:
            self._log_debug(err)
            return is_valid
        try:
            self.client.api.admin.adminDeleteUser(username=self.username)
            self.id = None
            return True
        except Exception as e:
            self._log_debug(e.response.content)
            return False

    @property
    def followers(self):
        result = []
        for follower in self.client.api.users.userListFollowers(username=self.username).json():
            user = self.client.users.new(username=follower['username'])
            for k, v in follower.items():
                setattr(user, k, v)
            result.append(user)
        return result

    @property
    def following(self):
        result = []
        for following in self.client.api.users.userListFollowing(username=self.username).json():
            user = self.client.users.new(username=following['username'])
            for k, v in following.items():
                setattr(user, k, v)
            result.append(user)
        return result

    def is_following(self, followee):
        try:
            self.client.api.users.userCheckFollowing(follower=self.username, followee=followee)
            return True
        except Exception as e:
            if e.response.status_code != 404:
                self._log_debug('username does not exist')
            return False

    @property
    def keys(self):
        if self.is_current:
            return GiteaUserCurrentPublicKeys(self.client, self)
        return GiteaPublicKeys(self.client, self)

    @property
    def gpg_keys(self):
        if self.is_current:
            return GiteaUserCurrentGpgKeys(self.client, self)
        return GiteaGpgKeys(self.client, self)

    @property
    def organizations(self):
        return GiteaOrgs(self.client, self)

    @property
    def repos(self):
        return GiteaRepos(self.client, self)

    @property
    def tokens(self):
        return GiteaTokens(self.client, self)

    @property
    def issues(self):
        return GiteaIssues(self.client, self)

    def __str__(self):
        return '\n<User>\n%s' % json.dumps(self.data, indent=4)

    __repr__ = __str__
