from .Ipmi import Ipmi

from Jumpscale import j

JSConfigBaseFactory = j.application.JSFactoryBaseClass

class IpmiFactory(JSConfigBaseFactory):
    """ Ipmi client factory

    Before using the ipmi client, make sure to install requirements.txt included in this directory
    """

    def __init__(self):
        self.__jslocation__ = "j.clients.ipmi"
        JSConfigBaseFactory.__init__(self, Ipmi)
