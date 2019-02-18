from Jumpscale import j

# TODO if we use ujson, then we need to refactor the rest of this file
# cause ujson has no JSEncoder propery
# try:
#     import ujson as json
# except BaseException:
# import json
import json
from .SerializerBase import SerializerBase


class BytesEncoder(json.JSONEncoder):

    ENCODING = 'ascii'

    def default(self, obj):
        if isinstance(obj, bytes):
            try:
                return obj.decode(self.ENCODING)
            except Exception as e:
                raise j.exceptions.Input("obj in json encoder has binary data which cannot be encoded")


        try:
            return json.JSONEncoder.default(self, obj)
        except Exception as e:
            raise j.exceptions.Input("obj in json encoder has binary data which cannot be encoded, default")


class Encoder(object):
    @staticmethod
    def get(encoding='ascii'):
        kls = BytesEncoder
        kls.ENCODING = encoding
        return kls


class SerializerUJson(SerializerBase):

    def __init__(self):
        SerializerBase.__init__(self)

    def dumps(self, obj, sort_keys=False, indent=False, encoding='ascii'):
        return json.dumps(obj, ensure_ascii=False, sort_keys=sort_keys, indent=indent, cls=Encoder.get(encoding=encoding))

    def loads(self, s):
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return json.loads(s)
