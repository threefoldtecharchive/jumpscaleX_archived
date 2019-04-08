from Jumpscale import j

JSConfigClient = j.application.JSBaseConfigClass

class SonicClient(JSConfigClient):

    _SCHEMATEXT = """
        @url =  jumpscale.zerohub.client
        name* = "" (S)
        """
    def _init(self):
        pass

    def start(self):
        pass

    def search(self, **kwargs):
        pass

    def add(self, **kwargs):
        pass