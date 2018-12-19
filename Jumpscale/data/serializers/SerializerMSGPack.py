
import msgpack
from .SerializerBase import SerializerBase
from Jumpscale import j


class SerializerMSGPack(SerializerBase):

    def __init__(self):
        SerializerBase.__init__(self)

    def dumps(self, obj):
        return msgpack.packb(obj, use_bin_type=True)

    def loads(self, s):
        return msgpack.unpackb(s, encoding="utf-8")
