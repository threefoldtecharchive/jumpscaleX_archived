import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaRepoRelease(j.application.JSBaseClass):
    def __init__(
            self,
            client,
            repo,
            id=None,
            assets=[],
            author=None,
            body=None,
            created_at=None,
            draft=None,
            name=None,
            prerelease=True,
            published_at=None,
            tag_name=None,
            tarball_url=None,
            target_commitish=None,
            url=None,
            zipball_url=None,
            user=None,

    ):
        self.client = client
        self.repo = repo
        self.created_at=created_at
        self.assets=assets
        self.author = author
        self.prerelease = prerelease
        self.draft=draft
        self.url = url
        self.id=id
        self.body = body
        self.tag_name = tag_name
        self.name = name
        self.published_at = published_at
        self.tarball_url = tarball_url
        self.target_commitish = target_commitish
        self.zipball_url = zipball_url
        self.user = user
        JSBASE.__init__(self)

    @property
    def data(self):
        d = {}

        for attr in [
            'id',
            'created_at',
            'updated_at',
            'assets',
            'prerelease',
            'author',
            'draft',
            'url',
            'body',
            'tag_name',
            'name',
            'published_at',
            'tarball_url',
            'target_commitish',
            'zipball_url',
        ]:
            v = getattr(self, attr)
            d[attr] = v
        return d


    def __repr__(self):
        return "Release %s" % json.dumps(self.data)

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
            resp = self.client.api.repos.repoCreateHook(data=self.data, repo=self.repo.name, owner=self.user.username)
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

            resp = self.client.api.repos.repoEditHook(data=self.data, repo=self.repo.name, owner=self.user.username, id=str(self.id))
            return True, ''
        except Exception as e:
            return False, e.response.content

    def delete(self, commit=True):
        is_valid, err = self._validate(delete=True)

        if not commit or not is_valid:
            return is_valid, err

        try:

            resp = self.client.api.repos.repoDeleteHook(repo=self.repo.name, owner=self.user.username,
                                                      id=str(self.id))
            return True, ''
        except Exception as e:
            return False, e.response.content

    __str__ = __repr__
