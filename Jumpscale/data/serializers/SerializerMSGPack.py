import msgpack
from .SerializerBase import SerializerBase
from Jumpscale import j


class SerializerMSGPack(SerializerBase):
    def __init__(self):
        SerializerBase.__init__(self)

    def dumps(self, obj):
        return msgpack.packb(obj, use_bin_type=True)

    def loads(self, s):
        if isinstance(s, (bytes, bytearray)):
            return msgpack.unpackb(s, raw=False)
        return False
