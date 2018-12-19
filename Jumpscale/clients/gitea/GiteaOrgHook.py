import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaOrgHook(JSBASE):
    def __init__(
            self,
            client,
            organization,
            id=None,
            type=None,
            content_type='json',
            url=None,
            events=[],
            active=True,
            updated_at=None,
            created_at=None
    ):
        self.client = client
        self.organization = organization
        self.created_at=created_at
        self.updated_at=updated_at
        self.active = active
        self.events = events
        self.content_type=content_type
        self.url = url
        self.type=type
        self.id=id
        JSBASE.__init__(self)

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'created_at',
            'updated_at',
            'active',
            'events',
            'type',
            'content_type',
            'url'
        ]:
            v = getattr(self, attr)
            d[attr] = v
        d['config'] = {'url': d['url'], 'content_type':d['content_type']}
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
                if not self.type:
                    is_valid = False
                    errors['type'] = 'Missing'

                if not self.type in ['gitea', 'gigs', 'slack', 'discord', 'dingtalk']:
                    is_valid = False
                    errors['type'] = 'Invalid type only allowed [gitea, gigs, slack, discor, dingtalk]'

                if not self.url:
                    is_valid = False
                    errors['url'] = 'Missing'

                if not self.content_type:
                    is_valid = False
                    errors['content_type'] = 'Missing'

                if not self.events:
                    is_valid = False
                    errors['events'] = 'Missing'

                for event in self.events:
                    if event not in ["create", "push", "pull_request"]:
                        is_valid = False
                        errors['evetns'] = 'Invalid event only allowed: ["create", "push", "pull_request"]'
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
            resp = self.client.api.orgs.orgCreateHook(data=self.data, org=self.organization.username)
            org = resp.json()
            config = org.pop('config')
            for k, v in org.items():
                setattr(self, k, v)
            self.url = config['url']
            self.content_type = config['content_type']

            return True, ''
        except Exception as e:
            return False, e.response.content

    def update(self, commit=True):
        is_valid, err = self._validate(update=True)

        if not commit or not is_valid:
            return is_valid, err

        try:

            resp = self.client.api.orgs.orgEditHook(data=self.data, id=str(self.id), org=self.organization.username)
            return True, ''
        except Exception as e:
            return False, e.response.content

    def delete(self, commit=True):
        is_valid, err = self._validate(delete=True)

        if not commit or not is_valid:
            return is_valid, err

        try:
            resp = self.client.api.orgs.orgDeleteHook(org=self.organization.username, id=str(self.id))
            return True, ''
        except Exception as e:
            return False, e.response.content

    def __repr__(self):
        return "Web hook %s" % json.dumps(self.data)

    __str__ = __repr__
