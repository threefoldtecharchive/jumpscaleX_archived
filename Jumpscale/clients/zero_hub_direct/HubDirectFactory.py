import os
from Jumpscale import j

from .HubDirectClient import HubDirectClient

JSConfigFactory = j.application.JSFactoryBaseClass


class HubDirectFactory(JSConfigFactory):
    """
    """
    __jslocation__ = "j.clients.zhubdirect"
    _CHILDCLASS = HubDirectClient

    def _init(self):
        self.__imports__ = "ovc"

    def generate(self):
        """
        generate the client out of the raml specs

        js_shell 'j.clients.zhubdirect.generate()'

        """
        path = j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")
        c = j.tools.raml.get(path)
        # c.specs_get('https://github.com/zero-os/hub-direct-server/tree/master/apidocs/api.raml') # broken...
        c.client_python_generate()
