from Jumpscale import j
from .OpenPublishClient import OpenPublishClient

JSConfigs = j.application.JSBaseConfigsClass


class OpenPublishFactory(JSConfigs):
    """
    Open Publish factory
    """
    __jslocation__ = "j.clients.open_publish"
    _CHILDCLASS = OpenPublishClient

    def __init__(self):
        JSConfigs.__init__(self)
        self._default = None

    @property
    def default(self):
        if not self._default:
            self._default = self.get("default")
        return self._default
