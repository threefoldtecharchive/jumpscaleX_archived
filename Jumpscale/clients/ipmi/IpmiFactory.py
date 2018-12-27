from .Ipmi import Ipmi

from Jumpscale import j

JSConfigBaseFactory = j.application.JSFactoryBaseClass


class IpmiFactory(JSConfigBaseFactory):
    """ Ipmi client factory

    Before using the ipmi client, make sure to install requirements.txt included in this directory
    """
    __jslocation__ = "j.clients.ipmi"
    _CHILDCLASS = Ipmi
