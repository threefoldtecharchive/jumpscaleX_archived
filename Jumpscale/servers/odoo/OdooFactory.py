from Jumpscale import j
from .OdooServer import OdooServer

JSConfigs = j.application.JSBaseConfigsClass


class OdooFactory(JSConfigs):
    """
    """

    __jslocation__ = "j.servers.odoo"
    _CHILDCLASS = OdooServer

    def _init(self, **kwargs):
        self._default = None

    @property
    def default(self):
        if not self._default:
            self._default = self.new(name="default")
        return self._default

    def install(self, reset=False):
        """
        kosmos 'j.servers.odoo.build()'
        """
        j.builders.apps.odoo.install(reset=reset)

    def test(self, start=True):
        """
        kosmos 'j.servers.odoo.test()'
        :return:
        """
        self.install()
        s = self.get(name="test")
        if start:
            s.start()

        for x in range(2):
            dbobj = s.databases.new()
            dbobj.name = "test%s" % x
            dbobj.admin_email = "info@example.com"
            dbobj.admin_passwd_ = "1234"
            dbobj.country_code = "be"
            dbobj.lang = "en_US"
            dbobj.phone = ""

        s.databases_create()

        s.save()

        cl1 = s.client_get("test1")
        cl2 = s.client_get("test2")

        cl1.modules_default_install()
        cl2.modules_default_install()

        # TODO: test how to create a contact
        # TODO: test how to get a contact & compare the content
        # TODO: test how to delete a contact
