from Jumpscale import j
from .ZeroStorFactory import ZeroStorFactory


JSBASE = j.application.JSBaseClass


class ZeroStorFactoryDeprecated(ZeroStorFactory, JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.clients.zerostor"
        JSBASE.__init__(self)
        self._log_warning("`j.clients.zerostor` is deprecated, please use `j.clients.zstor` instead")

        ZeroStorFactory.__init__(self)
