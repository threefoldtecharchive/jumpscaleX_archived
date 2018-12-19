from Jumpscale import j

from .webgateway import WebGateway

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class WebGatewayFactory(JSConfigBaseFactory):
    def __init__(self):
        self.__jslocation__ = "j.clients.webgateway"
        JSConfigBaseFactory.__init__(self, WebGateway)
