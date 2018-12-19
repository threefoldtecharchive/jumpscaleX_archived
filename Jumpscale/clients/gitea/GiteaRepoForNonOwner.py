import json
from Jumpscale import j

from .GiteaRepo import GiteaRepo

JSBASE = j.application.JSBaseClass


class GiteaRepoForNonOwner(GiteaRepo):
    pass
