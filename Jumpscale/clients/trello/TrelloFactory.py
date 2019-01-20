from Jumpscale import j
from .TrelloClient import TrelloClient
JSConfigs = j.application.JSBaseConfigsClass


class Trello(JSConfigs):
    __jslocation__ = 'j.clients.trello'
    _CHILDCLASS = TrelloClient

    def install(self, reset=False):
        j.builder.runtimes.pip.install("py-trello", reset=reset)

    def configure(self, instance="main", apikey="", secret="secret"):
        data = {}
        data["api_key_"] = apikey
        data["secret_"] = secret
        self.get(instance=instance, data=data)

    def test(self):
        """
        js_shell 'j.clients.trello.test()'

        to configure:
        js_config configure -l j.clients.trello

        get appkey: https://trello.com/app-key

        """
        cl = self.get(instance="main")
        cl.test()
