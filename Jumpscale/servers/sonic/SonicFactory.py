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
            self._default = self.get("default")
        return self._default
