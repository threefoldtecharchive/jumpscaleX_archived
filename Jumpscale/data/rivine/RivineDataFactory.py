from Jumpscale import j

from .RivineBinaryEncoder import RivineBinaryEncoder, RivineBinaryObjectEncoderBase
from .SiaBinaryEncoder import SiaBinaryEncoder, SiaBinaryObjectEncoderBase

class RivineDataFactory(j.application.JSBaseClass):
    """
    Tools to encode binary data for rivine
    """

    __jslocation__ = "j.data.rivine"

    @property
    def BaseRivineObjectEncoder(self):
        return RivineBinaryObjectEncoderBase

    @property
    def BaseSiaObjectEncoder(self):
        return SiaBinaryObjectEncoderBase

    def encoder_rivine_get(self):
        return RivineBinaryEncoder()

    def encoder_sia_get(self):
        return SiaBinaryEncoder()

    def test(self, name=''):
        """
        js_shell 'j.data.rivine.test()'
        :return:
        """
        self._test_run(name=name)
