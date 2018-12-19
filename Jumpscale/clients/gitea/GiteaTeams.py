from Jumpscale import j

from .GiteaTeam import GiteaTeam

JSBASE = j.application.JSBaseClass


class GiteaTeams(JSBASE):
    def __init__(self, client, organization):
        JSBASE.__init__(self)
        self.client = client
        self.organization = organization
        self.position = 0

    def new(self):
        return GiteaTeam(self.client, self.organization)

    def get(self, id, fetch=False):
        """

        """
        o = self.new()
        o.id = id
        if fetch:
            resp = self.client.api.teams.orgGetTeam(id=str(id)).json()
            config = resp.pop('config')
            for k, v in resp.items():
                setattr(o, k, v)
            o.url = config['url']
            o.content_type = config['content_type']
        return o

    def __next__(self):
        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            team = GiteaTeam(client=self.client, organization=self.organization)

            for k, v in item.items():
                setattr(team, k, v)
            return team
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.client.api.orgs.orgListTeams(self.organization.username).json()
        return self

    __str__ = __repr__ = lambda self: "Gitea Teams Iterator for organization: {0}".format(self.organization.username)

