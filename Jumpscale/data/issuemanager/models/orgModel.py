from Jumpscale import j

from data.capnp.ModelBase import ModelBase


class OrgModel(ModelBase):
    """
    Model Class for an org object
    """

    def index(self):
        self.collection.add2index(**self.to_dict())

    def memberSet(self, key, access):
        """
        @param key is the unique key of the member
        """
        member = j.clients.gogs.userCollection.get(key)

        for item in self.dbobj.members:
            if item.key == key:
                if item.access != access:
                    self.changed = True
                    item.access = access
                    item.name = member.dbobj.name
                return
        obj = self.collection.list_members_constructor(access=access, key=key, name=member.dbobj.name)
        self.addSubItem("members", obj)
        self.changed = True

    def memberAdd(self, userKey, access):
        """
        """
        obj = j.data.capnp.getMemoryObj(schema=self._capnp_schema.Member, userKey=userKey, access=access)

        self.dbobj.members.append(obj)
        self.save()

    def ownerSet(self, key):
        """
        """
        if key not in self.dbobj.owners:
            self.addSubItem("owners", key)
            self.changed = True

    def repoSet(self, key):
        """
        @param key, is the unique key of the repo
        """
        repo = j.clients.gogs.repoCollection.get(key)
        for item in self.dbobj.repos:
            if item.key == key:
                if item.name != repo.dbobj.name:
                    item.name = repo.dbobj.name
                    self.changed = True
                return
        obj = self.collection.list_repos_constructor(key=key, name=repo.dbobj.name)
        self.addSubItem("repos", obj)
        self.changed = True

    def gitHostRefSet(self, name, id):
        return j.clients.gogs._gitHostRefSet(self, name, id)

    def gitHostRefExists(self, name):
        return j.clients.gogs._gitHostRefExists(self, name)
