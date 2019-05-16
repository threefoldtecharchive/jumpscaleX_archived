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

    def rivine_encode(self, *values):
        e = self.encoder_rivine_get()
        e.add_all(*values)
        return e.data

    def sia_encode(self, *values):
        e = self.encoder_sia_get()
        e.add_all(*values)
        return e.data

    def test(self, name=""):
        """
        js_shell 'j.data.rivine.test()'
        :return:
        """
        self._test_run(name=name)
