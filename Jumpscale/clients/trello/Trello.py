from Jumpscale import j


TEMPLATE = """
api_key_ = ""
secret_ = ""
token_ = ""
token_secret_= ""
"""

JSConfigClient = j.application.JSBaseClass
JSConfigFactory = j.application.JSFactoryBaseClass


class TrelloClient(JSConfigClient):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        JSConfigClient.__init__(self, instance=instance,
                                data=data, parent=parent, template=TEMPLATE, interactive=interactive)

        from trello import TrelloClient

        if not self.config.data["token_secret_"]:
            print("**WILL TRY TO DO OAUTH SESSION")
            from trello.util import create_oauth_token
            access_token = create_oauth_token(key=self.config.data["api_key_"],secret=self.config.data["secret_"])
            self.config.data_set("token_",access_token["oauth_token"])
            self.config.data_set("token_secret_",access_token["oauth_token_secret"])

        self.client = TrelloClient(
            api_key=self.config.data["api_key_"],
            api_secret=self.config.data["secret_"],
             token=self.config.data["token_"],
            token_secret=self.config.data["token_secret_"]
        )

    def test(self):
    
        boards = self.client.list_boards()
        print(boards)


class Trello(JSConfigFactory):
    def __init__(self):
        self.__jslocation__ = 'j.clients.trello'
        JSConfigFactory.__init__(self, TrelloClient)

    def install(self, reset=False):
        j.tools.prefab.local.runtimes.pip.install("py-trello", reset=reset)

    def configure(self,instance="main",apikey="",secret="secret"):
        data={}
        data["api_key_"]=apikey
        data["secret_"]=secret
        self.get(instance=instance,data=data)

    def test(self):
        """
        js_shell 'j.clients.trello.test()'

        to configure:
        js_config configure -l j.clients.trello

        get appkey: https://trello.com/app-key

        """
        cl=self.get(instance="main")
        cl.test()
