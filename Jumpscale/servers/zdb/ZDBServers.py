from Jumpscale import j
from .ZDBServer import ZDBServer

JSConfigs = j.application.JSBaseConfigsClass


class ZDBServers(JSConfigs):
    """
    Open Publish factory
    """

    __jslocation__ = "j.servers.zdb"
    _CHILDCLASS = ZDBServer

    def _init(self, **kwargs):
        self._default = None

    @property
    def default(self):
        if not self._default:
            self._default = self.new(name="default")
        return self._default

    def build(self, reset=True):
        """
        kosmos 'j.servers.zdb.build()'
        """
        j.builders.db.zdb.install(reset=reset)

    def start_test_instance(
        self, destroydata=True, namespaces=[], admin_secret="123456", namespaces_secret="1234", restart=False
    ):
        """

        kosmos 'j.servers.zdb.start_test_instance(reset=True)'

        start a test instance with self.adminsecret 123456
        will use port 9901
        and name = test

        production is using other ports and other secret

        :return:
        """
        zdb = self.new(name="test")

        if destroydata:
            zdb.destroy()
            j.clients.redis._cache_clear()  # make sure all redis connections gone

        zdb.start()

        cla = zdb.client_admin_get()

        for ns in namespaces:
            if not cla.namespace_exists(ns):
                cla.namespace_new(ns, secret=namespaces_secret)
            else:
                if destroydata:
                    cla.namespace_delete(ns)
                    cla.namespace_new(ns, secret=namespaces_secret)

        if destroydata:
            j.clients.redis._cache_clear()  # make sure all redis connections gone

        return zdb

    def test(self, build=False):
        """
        kosmos 'j.servers.zdb.test(build=True)'
        kosmos 'j.servers.zdb.test()'
        """

        if build:
            self.build()
        zdb = self.start_test_instance(namespaces=["test"], restart=True, destroydata=True)

        cl = zdb.client_get(nsname="test")

        assert cl.ping()

        zdb.stop()
        zdb.destroy()

        print("TEST OK")
