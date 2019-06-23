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
        assert isinstance(obj, j.data.schema._JSXObjectClass)

        try:
            obj._cobj.clear_write_flag()
            data = obj._cobj.to_bytes_packed()
        except Exception as e:
            # need to catch exception much better (more narrow)
            obj._cobj_ = obj._cobj.as_builder()
            data = obj._cobj_.to_bytes_packed()

        if not model:
            assert not hasattr(obj, "sid") or obj.sid == 0  # when model not specified then sid should be 0
            version = 1
            data2 = version.to_bytes(1, "little") + bytes(bytearray.fromhex(obj._schema._md5)) + data
            j.core.db.hset("debug1", obj._schema._md5, "%s:%s:%s" % (obj.id, "", obj._schema.url))
        else:
            version = 10
            j.shell()
            data2 = version.to_bytes(2, "little") + version.to_bytes(obj._schema.sid, "little") + data
            j.core.db.hset("debug3", obj.model.sid, "%s:%s:%s" % (obj.id, obj._schema._md5, obj._schema.url))

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
        versionnr = int.from_bytes(data[0:1], byteorder="little")
        if versionnr == 1:
            md5bin = data[1:17]
            md5 = md5bin.hex()
            data2 = data[17:]
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
        elif versionnr == 10:
            sid = int.from_bytes(data[2:4], byteorder="little")
            data2 = data[4:]
            j.shell()
