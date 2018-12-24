from Jumpscale import j

from .Client import Client


class ZeroOSFactory(j.application.JSFactoryBaseClass):
    """
    """
    _CHILDCLASS = Client
    __jslocation__ = "j.clients.zos_protocol"

    def _init(self):
        self.connections = {}

    def get_from_itsyouonline(self,name="default",iyo_instance="default",host="localhost",port=6600):

        iyo = j.clients.itsyouonline.get(name=iyo_instance)
        passwd = iyo.jwt #there should be enough protection in here to refresh

        passwd = "'eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhenAiOiJGak1ja1NpcXRKSzhYWE5BUk5lYWtUb3dmeFZwIiwiZXhwIjoxNTQ1NzQzNDE5LCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJyZWZyZXNoX3Rva2VuIjoiVUJiS1F5enRkTm9wODZ4Z012aTUwNkVlQnFORyIsInNjb3BlIjpbInVzZXI6bWVtYmVyb2Y6dGYtcHJvZHVjdGlvbiJdLCJ1c2VybmFtZSI6ImRlc3BpZWdrIn0.X_sZnCEUShhENYqXKjRYJrA2H-uM_X1o3h_cq3GUlGPaySoiQopx3pA6LLrLFvHz9DunAwZKDJhNuHHLVRXAVVRqLAdhrT0qQdRrlOyi6EVo0uO7owtaDZAPcFkuUjhW'"


        cl = self.get(name=name,host=host,port=port,password=passwd,ssl=True)
        cl.ping()

    def test(self):
        """
        js_shell 'j.clients.zos_protocol.test()'
        :return:
        """


        # host = "127.0.0.1"
        # port = 6379
        # unixsocket = ""
        # password = ""  #can be the jwt
        # db = 0
        # ssl = true
        # timeout = 120


        cl = self.get_from_itsyouonline(name="test",host="10.102.54.126",port=6600)

        j.shell()


        #use j.clients.zoscmd... to start a local zos
        #connect client to zos do quite some tests
