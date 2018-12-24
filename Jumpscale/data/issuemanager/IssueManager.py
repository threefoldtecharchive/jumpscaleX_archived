
from Jumpscale import j

from tools.issuemanager.models.IssueModel import IssueModel
from tools.issuemanager.models.IssueCollection import IssueCollection
from tools.issuemanager.models.userModel import UserModel
from tools.issuemanager.models.userCollection import UserCollection
from tools.issuemanager.models.repoModel import RepoModel
from tools.issuemanager.models.repoCollection import RepoCollection
from tools.issuemanager.models.orgModel import OrgModel
from tools.issuemanager.models.orgCollection import OrgCollection
import capnp
from tools.issuemanager import model_capnp as ModelCapnp
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

JSBASE = j.application.JSBaseClass


class IssueManager(j.builder._BaseClass):

    """

    """

    def __init__(self):
        self.__jslocation__ = "j.tools.issuemanager"
        JSBASE.__init__(self)
        self.__imports__ = "pycapnp,peewee"
        self.namespace = "gogs"
        self.store = "gogs"
        # self.indexDBPath = ":memory:"
        self.indexDBPath = "/tmp/index.db"
        self._indexDB = None

    def destroyData(self):
        userCollection = self.getUserCollectionFromDB()
        userCollection.destroy()

        orgCollection = self.getOrgCollectionFromDB()
        orgCollection.destroy()

        issueCollection = self.getIssueCollectionFromDB()
        issueCollection.destroy()

        repoCollection = self.getRepoCollectionFromDB()
        repoCollection.destroy()

    def destroyTables(self):
        userCollection = self.getUserCollectionFromDB()
        userCollection.reset()

        orgCollection = self.getOrgCollectionFromDB()
        orgCollection.reset()

        issueCollection = self.getIssueCollectionFromDB()
        issueCollection.reset()

        repoCollection = self.getRepoCollectionFromDB()
        repoCollection.reset()

    def set_namespaceandstore(self, namespace="gogs", store="gogs"):
        self.namespace = namespace
        self.store = store

    def getIssueSchema(self):
        """
        Return capnp schema for issues struct
        """
        return ModelCapnp.Issue

    def getUserSchema(self):
        """
        Return capnp schema for user struct
        """
        return ModelCapnp.User

    def getRepoSchema(self):
        """
        Return capnp schema for repo struct
        """
        return ModelCapnp.Repo

    def getOrgSchema(self):
        """
        Return capnp schema for org struct
        """
        return ModelCapnp.Organization

    def getIssueCollectionFromDB(self, kvs=None):
        """
        std keyvalue stor is redis used by core
        """
        schema = self.getIssueSchema()
        if not kvs:
            kvs = j.data.kvs.getRedisStore(name=self.store, namespace=self.namespace + ":issue",
                                              unixsocket="%s/redis.sock" % j.dirs.TMPDIR)

        collection = j.data.capnp.getModelCollection(
            schema, namespace=self.namespace + ":issue", category="issues", modelBaseClass=IssueModel,
            modelBaseCollectionClass=IssueCollection, db=kvs, indexDb=kvs)
        return collection

    def getUserCollectionFromDB(self, kvs=None):
        schema = self.getUserSchema()
        if not kvs:
            kvs = j.data.kvs.getRedisStore(name=self.store, namespace=self.namespace + ":user",
                                              unixsocket="%s/redis.sock" % j.dirs.TMPDIR)

        collection = j.data.capnp.getModelCollection(
            schema, namespace=self.namespace + ":user", category="user", modelBaseClass=UserModel,
            modelBaseCollectionClass=UserCollection, db=kvs, indexDb=kvs)
        return collection

    def getRepoCollectionFromDB(self, kvs=None):
        schema = self.getRepoSchema()
        if not kvs:
            kvs = j.data.kvs.getRedisStore(name=self.store, namespace=self.namespace + ":repo",
                                              unixsocket="%s/redis.sock" % j.dirs.TMPDIR)

        collection = j.data.capnp.getModelCollection(
            schema, namespace=self.namespace + ":repo", category="repo", modelBaseClass=RepoModel,
            modelBaseCollectionClass=RepoCollection, db=kvs, indexDb=kvs)
        return collection

    def getOrgCollectionFromDB(self, kvs=None):
        schema = self.getOrgSchema()
        if not kvs:
            kvs = j.data.kvs.getRedisStore(name=self.store, namespace=self.namespace + ":org",
                                              unixsocket="%s/redis.sock" % j.dirs.TMPDIR)

        collection = j.data.capnp.getModelCollection(
            schema, namespace=self.namespace + ":org", category="orgs", modelBaseClass=OrgModel,
            modelBaseCollectionClass=OrgCollection, db=kvs, indexDb=kvs)
        return collection

    @property
    def indexDB(self):
        if self._indexDB is None:
            self._indexDB = SqliteExtDatabase(self.indexDBPath)
        return self._indexDB
