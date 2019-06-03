from .ZeroHubClient import ZeroHubClient
from Jumpscale import j

JSConfigs = j.application.JSBaseConfigsClass


class ZeroHubFactory(JSConfigs):
    __jslocation__ = "j.clients.zhub"
    _CHILDCLASS = ZeroHubClient

    def test(self):
        """
        js_shell 'j.clients.zhub.test()'
        """
        c = j.clients.zhub.test1
        c.name = "test1"
        c.token_ = "token"
        c.username = "test"
        c.save()

        assert j.clients.zhub.test1.name == "test1"
        assert j.clients.zhub.test1.username == "test"
