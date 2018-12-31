from Jumpscale import j
from .MySQLClient import MySQLClient
import mysql.connector
import time
import calendar

JSConfigFactory = j.application.JSFactoryBaseClass


class MySQLFactory(JSConfigFactory):
    """
    """
    __jslocation__ = "j.clients.mysql"

    def _init(self):
        self.clients = {}

    def get(self, ipaddr, port, login, passwd, dbname):
        return self.getClient(ipaddr, port, login, passwd, dbname)

    def getClient(self, ipaddr, port, login, passwd, dbname):
        key = "%s_%s_%s_%s_%s" % (ipaddr, port, login, passwd, dbname)
        if key not in self.clients:
            self.clients[key] = mysql.connector.connect(
                ipaddr, login, passwd, dbname, port=port)
        return MySQLClient(self.clients[key])
