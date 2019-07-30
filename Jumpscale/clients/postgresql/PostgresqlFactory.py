from Jumpscale import j
import psycopg2
from .PostgresqlClient import PostgresClient

JSConfigs = j.application.JSBaseConfigsClass


class PostgresqlFactory(JSConfigs):
    """
    """

    __jslocation__ = "j.clients.postgres"
    _CHILDCLASS = PostgresClient

    def install(self):
        """
        kosmos 'j.clients.postgres.install()'
        :return:
        """

    def start(self):
        j.builders.db.postgres.start()

    def stop(self):
        j.builders.db.postgres.stop()

    def db_client_get(self, name="test", dbname="main"):
        """
        returns database client

        cl = j.clients.postgres.db_client_get()

        login: root
        passwd: rooter
        dbname: main if not specified
        :return:
        """
        try:
            cl = self.get(name=name, ipaddr="localhost", port=5432, login="root", passwd_="rooter", dbname=dbname)
            r = cl.execute("SELECT version();")
            return cl
        except BaseException as e:
            pass

        # means could not return, lets now create the db
        j.sal.process.execute(
            """psql -h localhost -U postgres \
            --command='DROP ROLE IF EXISTS root; CREATE ROLE root superuser; ALTER ROLE root WITH LOGIN;' """
        )
        self.db_create(dbname)
        cl = self.get(name=name, ipaddr="localhost", port=5432, login="root", passwd_="rooter", dbname=dbname)
        cl.save()
        assert cl.client.status == True
        info = cl.client.info
        assert info.dbname == "main"
        return cl

    def test(self):
        """
        kosmos 'j.clients.postgres.test()'
        """
        self.install()
        self.start()

        cl = self.db_client_get()

        base, session = cl.sqlalchemy_client_get()
        j.shell()
        session.add(base.classes.address(email_address="foo@bar.com", user=(base.classes.user(name="foo"))))
        session.commit()

        # self.stop()
        print("TEST OK")
