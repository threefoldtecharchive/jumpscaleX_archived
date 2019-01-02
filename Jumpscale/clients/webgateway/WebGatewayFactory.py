from Jumpscale import j

from .webgateway import WebGateway

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class WebGatewayFactory(JSConfigBaseFactory):
    __jslocation__ = "j.clients.webgateway"
    _CHILDCLASS = WebGateway
