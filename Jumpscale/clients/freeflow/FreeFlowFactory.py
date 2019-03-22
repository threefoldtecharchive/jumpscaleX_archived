from Jumpscale import j
from .FreeFlowClient import FreeFlowClient
JSConfigs = j.application.JSBaseConfigsClass


class FreeFlowFactory(JSConfigs):
    __jslocation__ = 'j.clients.freeflowpages'
    _CHILDCLASS = FreeFlowClient

