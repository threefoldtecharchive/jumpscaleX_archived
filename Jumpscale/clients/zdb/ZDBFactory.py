import os
import uuid
from pprint import pprint

from Jumpscale import j

from .ZDBAdminClient import ZDBAdminClient
from .clients_impl import ZDBClientDirectMode, ZDBClientSeqMode, ZDBClientUserMode

JSBASE = j.application.JSBaseClass


_client_map = {
    'seq': ZDBClientSeqMode,
    'sequential': ZDBClientSeqMode,
    'user': ZDBClientUserMode,
    'direct': ZDBClientDirectMode,
}


#DO NOT USE THE CONFIG BASE CLASSES, OTHERWISE CHICKEN & EGG SITUATION !!!
class ZDBFactory(j.application.JSBaseClass):

    def __init__(self):
        self.__jslocation__ = "j.clients.zdb"
        JSBASE.__init__(self)

    def client_admin_get(self, addr="localhost", port=9900, secret="123456", mode='seq'):
        return ZDBAdminClient(addr=addr, port=port, secret=secret, mode=mode)

    def client_get(self, nsname="test", addr="localhost", port=9900, secret="1234", mode="seq"):
        """
        :param nsname: namespace name
        :param addr:
        :param port:
        :param secret:
        :return:
        """
        if mode not in _client_map:
            return ValueError("mode %s not supported" % mode)
        klass = _client_map[mode]
        return klass(addr=addr, port=port, secret=secret, nsname=nsname)

    def testdb_server_start_client_get(self, reset=False, admin_secret="123456",namespaces_secret="1234"):
        """
        js_shell 'j.clients.zdb.testdb_server_start_client_get(reset=True)'

        will start a ZDB server in tmux (will only start when not there yet or when reset asked for)
        erase all content
        and will return client to it

        """

        return j.servers.zdb.start_test_instance(destroydata=reset,admin_secret=admin_secret,
                                 namespaces_secret=namespaces_secret)

    def stop_test_instance(self):
        j.servers.zdb.stop()

    def test(self):
        """
        js_shell 'j.clients.zdb.test()'

        """


        cl = j.clients.zdb.testdb_server_start_client_get()

        self._test_run(name="base")
        self._test_run(name="admin")

        j.clients.zdb.stop_test_instance()



