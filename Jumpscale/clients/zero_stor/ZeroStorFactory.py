from .ZeroStorClient import ZeroStorClient
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class ZeroStorFactory(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.clients.zstor"
        self.__imports__ = "requests"
        JSBASE.__init__(self)

    def getClient(self):
        """
        # Getting client via accesstoken


        """
        return ZeroStorClient
