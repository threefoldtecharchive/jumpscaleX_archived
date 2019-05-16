from Jumpscale import j
import psycopg2
from .PostgresqlClient import PostgresClient

# import calendar
# from htmllib import HTMLParser
# from formatter import AbstractFormatter, DumbWriter
# from io import StringIO
# import lib.html


JSConfigs = j.application.JSBaseConfigsClass


class PostgresqlFactory(JSConfigs):
    """
    """

    __jslocation__ = "j.clients.postgres"
    _CHILDCLASS = PostgresClient

    def _init(self):
        self.__imports__ = "sqlalchemy"

    def db_create(self, db, ipaddr="localhost", port=5432, login="postgres", passwd="rooter"):
        """Create new database
        :param db: db name to be created
        :type db: str
        :param ipaddr: ip address,  defaults to "localhost"
        :type ipaddr: str
        :param port: port, defaults to 5432
        :type port: ipport
        :param login : postgres login, defaults to "postgres"
        :type login: str
        :param passwd: password associated with login, defaults to "rooter"
        :type passwd: str
        :raises j.exceptions.RuntimeError: Exception if db already exists
        """
        client = psycopg2.connect(
            "dbname='%s' user='%s' host='%s' password='%s' port='%s'" % ("template1", login, ipaddr, passwd, port)
        )
        cursor = client.cursor()
        client.set_isolation_level(0)
        try:
            cursor.execute("create database %s;" % db)
        except Exception as e:
            if str(e).find("already exists") != -1:
                pass
            else:
                raise j.exceptions.RuntimeError(e)
        client.set_isolation_level(1)

    def db_drop(self, db, ipaddr="localhost", port=5432, login="postgres", passwd="rooter"):
        """Drop a database
        :param db: db name to be dropped
        :type db: str
        :param ipaddr: ip address, defaults to "localhost"
        :type ipaddr: str, optional
        :param port: port, defaults to 5432
        :type port: ipport, optional
        :param login : postgres login, defaults to "postgres"
        :type login: str, optional
        :param passwd: password associated with login, defaults to "rooter"
        :type passwd: str, optional
        """
        args = {}
        args["db"] = db
        args["port"] = port
        args["login"] = login
        args["passwd"] = passwd
        args["ipaddr"] = ipaddr
        args["dbname"] = db
        cmd = "cd /opt/postgresql/bin;./dropdb -U %(login)s -h %(ipaddr)s -p %(port)s %(dbname)s" % (args)
        j.sal.process.execute(cmd, showout=False, die=False)
