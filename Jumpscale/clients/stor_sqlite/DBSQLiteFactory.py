from Jumpscale import j

from .DBSQLite import DBSQLite


class DBSQLiteFactory(j.application.JSBaseFactoryClass):

    __jslocation__ = "j.clients.sqlitedb"

    def client_get(self, nsname="test", fromcache=True, **kwargs):
        """
        :param nsname: namespace name
        :return:
        """
        return DBSQLite(nsname=nsname)

    def test(self):
        """
        kosmos 'j.clients.sqlitedb.test()'

        """

        self._test_run(name="base")
