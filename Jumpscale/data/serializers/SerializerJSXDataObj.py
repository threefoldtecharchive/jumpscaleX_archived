from Jumpscale import j
from .SerializerBase import SerializerBase


class SerializerJSXDataObj(SerializerBase):
    def __init__(self):
        SerializerBase.__init__(self)

    def dumps(self, obj, model=None, test=True):
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
        data2 = version.to_bytes(2, "little") + bytes(bytearray.fromhex(obj._schema._md5)) + data

        if test:
            # if not md5 in j.data.schema.md5_to_schema:
            self.loads(data=data2)
            if model:
                j.shell()

        return data2

    def loads(self, data, model=None):
        """
        j.data.serializers.jsxdata.loads(..
        :param data:
        :return: obj
        """
        versionnr = int.from_bytes(data[0:2], byteorder="little")
        assert versionnr == 1
        md5bin = data[2:18]
        md5 = md5bin.hex()
        data2 = data[18:]
        if md5 in j.data.schema.md5_to_schema:
            schema = j.data.schema.md5_to_schema[md5]
            obj = schema.get(capnpdata=data2, model=model)
            return obj
        else:
            j.shell()
            if not model:
                raise RuntimeError("could not find schema with md5:%s, no model specified" % md5)
            j.shell()
            raise RuntimeError("could not find schema with md5:%s" % md5)
