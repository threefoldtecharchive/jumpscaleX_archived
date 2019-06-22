from Jumpscale import j
from .SerializerBase import SerializerBase


class SerializerJSXDataObj(SerializerBase):
    def __init__(self):
        SerializerBase.__init__(self)

    def dumps(self, obj, model=None, test=False):
        """
        obj is the dataobj for JSX

        j.data.serializers.jsxdata.dumps(..

        :param obj:
        :param test: if True will be slow !!!
        :return:
        """
        assert isinstance(obj, j.data.schema.DataObjBase)

        try:
            obj._cobj.clear_write_flag()
            data = obj._cobj.to_bytes_packed()
        except Exception as e:
            # need to catch exception much better (more narrow)
            obj._cobj_ = obj._cobj.as_builder()
            data = obj._cobj_.to_bytes_packed()
        version = 1
        data2 = version.to_bytes(1, "little") + bytes(bytearray.fromhex(obj._schema._md5)) + data

        if test and model:
            # if not md5 in j.data.schema.md5_to_schema:
            j.shell()
            w

        return data2

    def loads(self, data, model=None):
        """
        j.data.serializers.jsxdata.loads(..
        :param data:
        :return: obj
        """
        versionnr = int.from_bytes(data[0:1], byteorder="little")
        assert versionnr == 1
        md5bin = data[1:17]
        md5 = md5bin.hex()
        data2 = data[17:]
        if md5 in j.data.schema.md5_to_schema:
            schema = j.data.schema.md5_to_schema[md5]
            obj = schema.get(serializeddata=data2, model=model)
            return obj
        else:
            if not model:
                raise RuntimeError("could not find schema with md5:%s, no model specified" % md5)
            j.shell()
            raise RuntimeError("could not find schema with md5:%s" % md5)
