from Jumpscale import j
import psycopg2
from .PostgresqlClient import PostgresClient
# import calendar
# from htmllib import HTMLParser
# from formatter import AbstractFormatter, DumbWriter
# from io import StringIO
# import lib.html


JSConfigFactory = j.application.JSFactoryBaseClass


class PostgresqlFactory(JSConfigFactory):
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
        :param ipaddr: ip address
        :type ipaddr: str
        :param port: port
        :type port: ipport
        :param login : postgres login
        :type login: str
        :param passwd: password associated with login
        :type passwd: str
        :raises j.exceptions.RuntimeError: Exception if db already exists
        """
        client = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (
            "template1", login, ipaddr, passwd, port))
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
        :param ipaddr: ip address
        :type ipaddr: str
        :param port: port
        :type port: ipport
        :param login : postgres login
        :type login: str
        :param passwd: password associated with login
        :type passwd: str
        """
        args = {}
        args["db"] = db
        args["port"] = port
        args["login"] = login
        args["passwd"] = passwd
        args["ipaddr"] = ipaddr
        args["dbname"] = db
        cmd = "cd /opt/postgresql/bin;./dropdb -U %(login)s -h %(ipaddr)s -p %(port)s %(dbname)s" % (
            args)
        j.sal.process.execute(cmd, showout=False, die=False)
