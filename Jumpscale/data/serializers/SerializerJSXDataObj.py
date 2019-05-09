
from Jumpscale import j
from .SerializerBase import SerializerBase


class SerializerJSXDataObj(SerializerBase):
    def __init__(self):
        SerializerBase.__init__(self)

    def dumps(self, obj):
        """
        obj is the dataobj for JSX

        j.data.serializers.jsxdata.dumps(..

        :param obj:
        :return:
        """
        assert isinstance(obj,j.data.schema.DataObjBase)
        return obj._data


    def loads(self, data,model=None):
        """
        j.data.serializers.jsxdata.loads(..
        :param data:
        :return: obj
        """
        versionnr = int.from_bytes(data[0:1],byteorder='little')
        md5bin = data[1:17]
        md5 = md5bin.hex()
        data2 = data[17:]
        if md5 in j.data.schema.md5_to_schema:
            schema = j.data.schema.md5_to_schema[md5]
            obj = schema._get(data2, model=model)
            return obj
        else:
            raise RuntimeError("could not find schema with md5:%s"%md5)


