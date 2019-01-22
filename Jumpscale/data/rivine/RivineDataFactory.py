from Jumpscale import j

from RivineBinaryEncoder import RivineBinaryEncoder
from SiaBinaryEncoder import SiaBinaryEncoder

class RivineDataFactory(j.application.JSBaseClass):
    """
    Tools to encode binary data for rivine
    """
    __jslocation__ = "j.data.rivine"

    def encoder_rivine_bin_get(self):
        return RivineBinaryEncoder()


    def encoder_sia_bin_get(self):
        return SiaBinaryEncoder()

    def test(self):
        """
        js_shell 'j.data.rivine.test()'
        :return:
        """
        j.shell()
