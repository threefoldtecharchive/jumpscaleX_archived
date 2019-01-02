from Jumpscale import j
from .GraphiteClient import GraphiteClient
JSConfigFactory = j.application.JSFactoryBaseClass


class GraphiteFactory(JSConfigFactory):

    __jslocation__ = "j.clients.graphite"
    _CHILDCLASS = GraphiteClient
