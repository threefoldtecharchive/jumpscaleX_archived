from Jumpscale import j
from .peeweeClient import PeeweeClient

import importlib
from peewee import *
import uuid


class PeeweeFactory(j.application.JSBaseConfigsClass):
    """
    """

    __jslocation__ = "j.clients.peewee"
    _CHILDCLASS = PeeweeClient

    def _init(self, **kwargs):
        self.__imports__ = "peewee"
        self.clients = {}

        from peewee import (
            PrimaryKeyField,
            BlobField,
            Model,
            BooleanField,
            TextField,
            CharField,
            IntegerField,
            SqliteDatabase,
            FloatField,
            DateTimeField,
            ForeignKeyField,
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
        cl.db_create("pewee_test")
        pw = self.get(name="test", dbname="pewee_test", passwd_="123456")
        db = pw.db
        pw.save()

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
        u.username = uuid.uuid4().hex[:6].upper()
        u.save()
        m = pw.model_get()
        return "TESTS OK"
