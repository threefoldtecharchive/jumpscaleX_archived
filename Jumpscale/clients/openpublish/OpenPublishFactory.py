from Jumpscale import j
from .OpenPublishClient import OpenPublishClient

JSConfigs = j.application.JSBaseConfigsClass


class OpenPublishFactory(JSConfigs):
    """
    Open Publish factory
    """
    __jslocation__ = "j.clients.open_publish"
    _CHILDCLASS = OpenPublishClient
