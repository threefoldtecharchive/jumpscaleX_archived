import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaRepoPublicKey(j.application.JSBaseClass):
    def __init__(self, user, repo, id=None, key=None, title=None, created_at=None, fingerprint=None, url=None):
        JSBASE.__init__(self)
        self.user = user
        self.id = id
        self.key = key
        self.title = title
        self.created_at = created_at
        self.fingerprint = fingerprint
        self.url = url
        self.repo = repo

    @property
    def data(self):
        d = {}
        for attr in ["id", "key", "title", "created_at", "fingerprint", "url"]:
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

        operation = "create"

        if create:

            if self.id:
                is_valid = False
                errors["id"] = "Already existing"
            else:
                if not self.user.username:
                    is_valid = False
                    errors["user"] = {"username": "Missing"}

                if not self.key:
                    is_valid = False
                    errors["key"] = "Missing"

                if not self.title:
                    is_valid = False
                    errors["title"] = "Missing"

        elif delete:
            operation = "delete"
            if not self.id:
                is_valid = False
                errors["id"] = "Missing"

        if is_valid:
            return True, ""

        return False, "{0} Error ".format(operation) + json.dumps(errors)

    def save(self, commit=True):
        """
        Create public key for user
        """
        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            return is_valid, err
        try:

            resp = self.user.client.api.repos.repoCreateKey(self.data, repo=self.repo.name, owner=self.user.username)
            pubkey = resp.json()
            for k, v in pubkey.items():
                setattr(self, k, v)
            return True, ""
        except Exception as e:
            return False, e.response.content

    def delete(self, commit=True):
        is_valid, err = self._validate(delete=True)

        if not commit or not is_valid:
            return is_valid, err
        try:
            self.user.client.api.repos.repoDeleteKey(owner=self.user.username, id=str(self.id), repo=self.repo.name)
            return True, ""
        except Exception as e:
            return False, e.response.content

    __str__ = __repr__ = lambda self: json.dumps(self.data)
