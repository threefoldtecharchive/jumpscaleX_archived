from Jumpscale import j
from .TrelloClient import TrelloClient

JSConfigs = j.application.JSBaseConfigsClass


class Trello(JSConfigs):
    __jslocation__ = "j.clients.trello"
    _CHILDCLASS = TrelloClient

    def install(self, reset=False):
        j.builder.runtimes.pip.install("py-trello", reset=reset)

    def test(self):
        """
        kosmos 'j.clients.trello.test()'

        to configure:
        js_config configure -l j.clients.trello

        get appkey: https://trello.com/app-key

        """
        cl = self.get(name="main")
        cl.test()
