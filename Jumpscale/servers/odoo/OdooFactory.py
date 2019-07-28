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
        s = self.get(name="test_instance")
        s.save()
        if start:
            s.start()

        client = s.default_client

        # TODO: ... start odoo, connect client to it

        client.module_install
        client.user_add
