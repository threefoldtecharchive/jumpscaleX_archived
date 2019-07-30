from Jumpscale import j
from .peeweeClient import PeeweeClient

import importlib
from .peewee import *


class PeeweeFactory(j.application.JSBaseConfigsClass):
    """
    """

    __jslocation__ = "j.clients.peewee"
    _CHILDCLASS = PeeweeClient

    def _init(self, **kwargs):
        self.__imports__ = "peewee"
        self.clients = {}

        from .peewee import (
            PrimaryKeyField,
            BlobField,
            Model,
            BooleanField,
            TextField,
            CharField,
            IntegerField,
            SqliteDatabase,
            FloatField,
        )

        self.PrimaryKeyField = PrimaryKeyField
        self.DateTimeField = DateTimeField
        self.BlobField = BlobField
        self.Model = Model
        self.BooleanField = BooleanField
        self.TextField = TextField
        self.CharField = CharField
        self.IntegerField = IntegerField
        self.SqliteDatabase = SqliteDatabase
        self.FloatField = FloatField
        self.ForeignKeyField = ForeignKeyField

    def test_model_create(self, psqlclient):
        pass

    def test(self):
        """
        kosmos 'j.clients.peewee.test()'
        :return:
        """

        j.builders.db.postgres.start()
        cl = j.clients.postgres.db_client_get()
        pw = cl.peewee_client_get()
        db = pw.db

        class BaseModel(self.Model):
            class Meta:
                database = db

        class User(BaseModel):
            username = self.TextField(unique=True)

            class Meta:
                table_name = "user"

        class Tweet(BaseModel):
            content = self.TextField()
            timestamp = self.DateTimeField()
            user = self.ForeignKeyField(column_name="user_id", field="id", model=User)

            class Meta:
                table_name = "tweet"

        with db:
            db.create_tables([User, Tweet])

        u = User()
        u.username = "sss"
        u.save()

        m = pw.model_get()
        j.shell()
