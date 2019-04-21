from Jumpscale import j
from .SonicClient import SonicClient
JSConfigs = j.application.JSBaseConfigsClass

class SonicFactory(JSConfigs):

    """
    Sonic Client factory
    """

    __jslocation__ = "j.clients.sonic"
    _CHILDCLASS = SonicClient

    def _init(self):
        pass

    def test1(self):
        data = {
            'post:1': "this is some test text hello",
            'post:2': 'this is a hello world post',
            'post:3': "hello how is it going?",
            'post:4': "for the love of god?",
            'post:5': "for the love lorde?",
        }
        client = j.clients.sonic.new('sonicmain', host="127.0.0.1", port=1491, password='dmdm')
        for articleid, content in data.items():
            client.push("forum", "posts", articleid, content)
        print(client.query("forum", "posts", "hello"))
        print(client.query("forum", "posts", "love"))
        print(client.query("forum", "posts", "world"))
