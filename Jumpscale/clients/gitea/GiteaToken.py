import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaToken(j.application.JSBaseClass):

    def __init__(
            self,
            client,
            user,
            id=None,
            name=None,
    ):
        JSBASE.__init__(self)
        self.user = user
        self.client = client
        self.id = id
        self.name = name

    @property
    def data(self):
        d = {}
        for attr in [
            'id',
            'name',
        ]:
            v = getattr(self, attr)
            d[attr] = v
        return d

    def _validate(self, create=False, delete=False):
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
                    errors['user'] = {'username': 'Missing'}

                if not self.name:
                    is_valid = False
                    errors['name'] = 'Missing'


        elif delete:
            operation = 'delete'
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
            self._logger.debug(err)
            return is_valid

        try:
            # user object used doesn doesn't belong to user using gitea client
            # try using admin
            if not self.user.is_current:
                return False
            else:
                resp = self.user.client.api.users.userCreateToken(data=self.data, name=self.name, username=self.user.username)
            token = resp.json()
            for k, v in token.items():
                setattr(self, k, v)
            return True, ''
        except Exception as e:
            if e.response.status_code == 401:
                self._logger.debug('not authorized')
                self._logger.error('#FIX ME: THIS API not working')
            return False

    def __repr__ (self):
        return '\n<Token name={0}>\n{1}'.format(
            self.name,
            json.dumps(self.data, indent=4)
        )

    __str__ = __repr__


