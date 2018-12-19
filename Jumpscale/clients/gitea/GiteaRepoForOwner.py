import json

from Jumpscale import j

from .GiteaRepo import GiteaRepo

JSBASE = j.application.JSBaseClass


class GiteaRepoForOwner(GiteaRepo):

    def __str__(self):
        return '\n<Repo: owned by current user: %s>\n%s' % (self.user.username, json.dumps(self.data, indent=4))

    __repr__ = __str__
