from .GoogleCompute import GoogleCompute
from Jumpscale import j
JSBASE = j.application.JSFactoryBaseClass


class GoogleComputeFactory(JSBASE):
    __jslocation__ = "j.clients.google_compute"
    _CHILDCLASS = GoogleCompute
