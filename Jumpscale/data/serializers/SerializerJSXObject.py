from Jumpscale import j
from .SerializerBase import SerializerBase


class SerializerJSXObject(SerializerBase):
    def __init__(self):
        SerializerBase.__init__(self)

    def dumps(self, obj, model=None, test=False, remote=False):
        """
        obj is the dataobj for JSX

        j.data.serializers.jsxdata.dumps(..

        :param obj:
        :param test: if True will be slow !!!
        :return:
        """
        assert isinstance(obj, j.data.schema._JSXObjectClass)
        if model:
            assert isinstance(model, j.data.bcdb._BCDBModelClass)

        try:
            obj._capnp_obj.clear_write_flag()
            data = obj._capnp_obj.to_bytes_packed()
        except Exception as e:
            # need to catch exception much better (more narrow)
            obj._capnp_obj_ = obj._capnp_obj.as_builder()
            data = obj._capnp_obj_.to_bytes_packed()

        if not model and not remote:
            version = 1
            data2 = version.to_bytes(1, "little") + bytes(bytearray.fromhex(obj._schema._md5)) + data
        elif remote:
            version = 2
            if obj.id:
                objid = obj.id
            else:
                objid = 0
            data2 = (
                version.to_bytes(1, "little")
                + objid.to_bytes(4, "little")
                + bytes(bytearray.fromhex(obj._schema._md5))
                + data
            )
        else:
            objid = None
            version = 10
            sid = obj._model.sid
            assert isinstance(sid, int)
            assert sid > 0
            data2 = version.to_bytes(1, "little") + sid.to_bytes(2, "little") + data

        if test:
            # if not md5 in j.data.schema.md5_to_schema:
            if remote:
                u = self.loads(data=data2)
                assert u.id == objid
            else:
                self.loads(data=data2, model=model)

        # self._log_debug("DUMPS:%s:%s" % (version, obj.id), data=obj._ddict)

        return data2

    def loads(self, data, model=None):
        """
        j.data.serializers.jsxdata.loads(..
        :param data:
        :return: obj
        """
        assert data
        if model:
            assert isinstance(model, j.data.bcdb._BCDBModelClass)
        versionnr = int.from_bytes(data[0:1], byteorder="little")
        if versionnr in [1, 2]:

            if versionnr == 1:
                md5bin = data[1:17]
                md5 = md5bin.hex()
                data2 = data[17:]
                obj_id = None

            elif versionnr == 2:
                obj_id = int.from_bytes(data[1:5], byteorder="little")
                md5bin = data[5:21]
                md5 = md5bin.hex()
                data2 = data[21:]

            # self._log_debug("LOADS:%s:%s" % (versionnr, obj_id))

            if md5 in j.data.schema.md5_to_schema:
                schema = j.data.schema.md5_to_schema[md5]
                obj = schema.new(capnpdata=data2, model=model)
                if versionnr == 2:
                    obj.id = obj_id
                    if obj.id == 0:
                        obj.id = None
                return obj
            else:
                if not model:
                    raise j.exceptions.Base("could not find schema with md5:%s, no model specified" % md5)
                raise j.exceptions.Base("could not find schema with md5:%s" % md5)

        elif versionnr == 10:
            if not model:
                raise j.exceptions.Base("model needs to be specified")
            sid = int.from_bytes(data[1:3], byteorder="little")
            data2 = data[3:]
            model2 = model.bcdb.model_get_from_sid(sid)  # weird concept but it could be we get other model based on sid
            return model2.schema.new(capnpdata=data2, model=model)
        else:

            raise j.exceptions.Base("version wrong, versionnr found:%s (needs to be 1 or 10)" % versionnr)
