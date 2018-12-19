from Jumpscale import j


JSBASE = j.application.JSBaseClass


class GiteTeamMembers(JSBASE):
    def __init__(self, client, team):
        JSBASE.__init__(self)
        self.client = client
        self.team = team
        self.position = 0

    def add(self, username):
        try:
            resp = self.client.api.teams.orgAddTeamMember(username=username, id=str(self.team.id))
            return True, ''
        except Exception as e:
            if e.response.status_code == 404:
                return False, 'Not found'
            return False, e.response.content

    def remove(self, username):
        try:
            resp = self.client.api.teams.orgDeleteTeamMember(username=username, id=str(self.team.id))
            return True, ''
        except Exception as e:
            if e.response.status_code == 404:
                return False, 'Not found'
            return False, e.response.content

    def __next__(self):
        from JumpScale9Lib.clients.gitea.GiteaUser import GiteaUser

        if self.position < len(self._items):
            item = self._items[self.position]
            self.position += 1
            member = GiteaUser(client=self.client)
            for k, v in item.items():
                setattr(member, k, v)
            return member
        else:
            self.position = 0
            raise StopIteration()

    def __iter__(self):
        self._items = self.client.api.teams.orgListTeamMembers(str(self.team.id)).json()
        return self

    __str__ = __repr__ = lambda self: "Gitea Members Iterator for team: {0}".format(self.team.id)

