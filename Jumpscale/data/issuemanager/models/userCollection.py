from Jumpscale import j

from data.capnp.ModelBaseCollection import ModelBaseCollection

from peewee import *
import peewee
import operator
from playhouse.sqlite_ext import Model

# from playhouse.sqlcipher_ext import *
# db = Database(':memory:')


class UserCollection(ModelBaseCollection):
    """
    This class represent a collection of users
    """

    def _getModel(self):
        class User(Model):
            key = CharField(index=True, default="")
            gitHostRefs = CharField(index=True, default="")
            name = CharField(index=True, default="")
            fullname = CharField(index=True, default="")
            email = CharField(index=True, default="")
            inGithub = BooleanField(index=True, default=False)
            githubId = CharField(index=True, default="")
            telegramId = CharField(index=True, default="")
            iyoId = CharField(index=True, default="")
            modTime = TimestampField(index=True, default=j.data.time.epoch)

            class Meta:
                database = j.tools.issuemanager.indexDB
                # order_by = ["id"]

        return User

    def _init(self, **kwargs):
        # init the index
        db = j.tools.issuemanager.indexDB

        User = self._getModel()

        self.index = User

        if db.is_closed():
            db.connect()
        db.create_tables([User], True)

    def reset(self):
        db = j.tools.issuemanager.indexDB
        db.drop_table(self._getModel())

    def add2index(self, **args):
        """
        key = CharField(index=True, default="")
        gitHostRefs = CharField(index=True, default="")
        name = CharField(index=True, default="")
        fullname = CharField(index=True, default="")
        email = CharField(index=True, default="")
        inGithub = BooleanField(index=True, default=False)
        githubId = CharField(index=True, default="")
        telegramId = CharField(index=True, default="")
        iyoId = CharField(index=True, default="")
        modTime = TimestampField(index=True, default=j.data.time.epoch)


        @param args is any of the above
        """

        if "gitHostRefs" in args:
            args["gitHostRefs"] = ["%s_%s_%s" % (item["name"], item["id"], item["url"]) for item in args["gitHostRefs"]]

        args = self._arraysFromArgsToString(["gitHostRefs"], args)

        # this will try to find the right index obj, if not create

        obj, isnew = self.index.get_or_create(key=args["key"])

        for key, item in args.items():
            if key in obj._data:
                obj._data[key] = item

        obj.save()

    def getFromGitHostID(self, git_host_name, git_host_id, git_host_url, createNew=True):
        return j.clients.gogs._getFromGitHostID(
            self, git_host_name=git_host_name, git_host_id=git_host_id, git_host_url=git_host_url, createNew=createNew
        )

    def list(self, **kwargs):
        """
        List all keys of a index


        list all entries matching kwargs. If none are specified, lists all

        e.g.
        email="reem@threefold.tech", name="reem"

        """
        if kwargs:
            clauses = []
            for key, val in kwargs.items():
                if not hasattr(self.index, key):
                    raise j.exceptions.Base('%s model has no field "%s"' % (self.index._meta.name, key))
                field = getattr(self.index, key)
                clauses.append(field.contains(val))

            res = [
                item.key
                for item in self.index.select()
                .where(peewee.reduce(operator.and_, clauses))
                .order_by(self.index.modTime.desc())
            ]
        else:
            res = [item.key for item in self.index.select().order_by(self.index.modTime.desc())]

        return res

    def destroy(self):
        self._db.destroy()
        self._index.destroy()
        self.index.truncate_table()
