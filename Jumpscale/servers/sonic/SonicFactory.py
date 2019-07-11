from Jumpscale import j
from .SonicServer import SonicServer

JSConfigs = j.application.JSBaseConfigsClass


class SonicFactory(JSConfigs):
    """
    Open Publish factory
    """

    __jslocation__ = "j.servers.sonic"
    _CHILDCLASS = SonicServer

    def __init__(self):
        JSConfigs.__init__(self)
        self._default = None

    @property
    def default(self):
        if not self._default:
            self._default = self.new(name="default")
        return self._default

    def install(self, reset=True):
        """
        kosmos 'j.servers.sonic.build()'
        """
        j.builders.apps.sonic.install(reset=reset)

    def test(self):
        """
        kosmos 'j.servers.sonic.test()'
        :return:
        """

        # TODO: start sonic and test sonic through the client

        s = self.new("test")
        s.start()

        cl = s.default_client

        pass
