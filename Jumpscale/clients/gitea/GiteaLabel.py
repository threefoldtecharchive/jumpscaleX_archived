import json
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class GiteaLabel(j.application.JSBaseClass):
    def __init__(self, client, repo, user, id=None, color=None, name=0, url=None):
        JSBASE.__init__(self)
        self.client = client
        self.repo = repo
        self.user = user
        self.id = id
        self.color = color
        self.name = name
        self.url = url

    @property
    def data(self):
        d = {}
        for attr in ["id", "name", "color", "url"]:
            v = getattr(self, attr)
            d[attr] = v
        return d

    def _validate(self, create=False, update=False, delete=False):
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
                if not self.name:
                    is_valid = False
                    errors["name"] = "Missing"
                if not self.color:
                    is_valid = False
                    errors["color"] = "Missing"

        elif update:
            operation = "update"
            if not self.id:
                is_valid = False
                errors["id"] = "Missing"
        elif delete:
            operation = "delete"
            if not self.id:
                is_valid = False
                errors["id"] = "Missing"

        if is_valid:
            return True, ""

        return False, "{0} Error ".format(operation) + json.dumps(errors)

    def save(self, commit=True):
        is_valid, err = self._validate(create=True)

        if not commit or not is_valid:
            return is_valid, err

        try:
            resp = self.client.api.repos.issueCreateLabel(data=self.data, repo=self.repo.name, owner=self.user.username)

            c = resp.json()
            for k, v in c.items():
                setattr(self, k, v)
            return True, ""
        except Exception as e:
            return False, e.response.content

    def update(self, commit=True):
        is_valid, err = self._validate(update=True)

        if not commit or not is_valid:
            return is_valid, err

        try:
            username = self.user["username"] if type(self.user) == dict else self.user.username
            repo = self.repo["name"] if type(self.repo) == dict else self.repo.name
            resp = self.client.api.repos.issueEditLabel(data=self.data, id=str(self.id), repo=repo, owner=username)
            return True, ""
        except Exception as e:
            return False, e.response.content

    def delete(self, commit=True):
        is_valid, err = self._validate(delete=True)

        if not commit or not is_valid:
            return is_valid, err

        try:
            username = self.user["username"] if type(self.user) == dict else self.user.username
            repo = self.repo["name"] if type(self.repo) == dict else self.repo.name
            resp = self.client.api.repos.issueDeleteLabel(id=str(self.id), repo=repo, owner=username)
            return True, ""
        except Exception as e:
            return False, e.response.content

    def __repr__(self):
        return "Label %s" % json.dumps(self.data)

    __str__ = __repr__
