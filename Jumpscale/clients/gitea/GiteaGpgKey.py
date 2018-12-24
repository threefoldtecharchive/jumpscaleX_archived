import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaGpgKey(j.application.JSBaseClass):

    def __init__(
            self,
            client,
            user,
            id=None,
            can_certify=True,
            can_encrypt_comms=True,
            can_sign=True,
            emails=[],
            expires_at=None,
            key_id=None,
            can_encrypt_storage=True,
            created_at=None,
            primary_key_id=None,
            public_key=None,
            subkeys=[],
    ):
        JSBASE.__init__(self)
        self.user = user
        self.client = client
        self.id = id
        self.can_encrypt_comms = can_encrypt_comms
        self.can_sign = can_sign
        self.created_at = created_at
        self.emails=emails
        self.can_certify = can_certify
        self.expires_at=expires_at
        self.key_id=key_id
        self.can_encrypt_storage=can_encrypt_storage
        self.primary_key_id=primary_key_id
        self.public_key=public_key
        self.subkeys = subkeys

    @property
    def data(self):
        d = {}
        for attr in [
            'id',
            'can_encrypt_comms',
            'can_certify',
            'created_at',
            'can_sign',
            'emails',
            'expires_at',
            'key_id',
            'can_encrypt_storage',
            'created_at',
            'primary_key_id',
            'public_key',
            'subkeys'
        ]:
            v = getattr(self, attr)
            if v:
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

                if not self.public_key:
                    is_valid = False
                    errors['public_key'] = 'Missing'

        elif delete:
            operation = 'delete'
            if not self.id:
                is_valid = False
                errors['id'] = 'Missing'

        if is_valid:
            return True, ''

        return False, '{0} Error '.format(operation) + json.dumps(errors)


    def __repr__ (self):
        return '\n<GPG Key: user={0}>\n{1}'.format(
            self.user.username,
            json.dumps(self.data, indent=4)
        )

    __str__ = __repr__
