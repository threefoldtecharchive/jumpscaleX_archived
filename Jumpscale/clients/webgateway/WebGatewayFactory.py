from Jumpscale import j
from .webgateway import WebGateway


class WebGatewayFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = "j.clients.webgateway"
    _CHILDCLASS = WebGateway
