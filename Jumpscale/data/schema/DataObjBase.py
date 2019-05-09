from Jumpscale import j


class DataObjBase:
    def __init__(self, data=None, schema=None, model=None):
        self._cobj_ = None
        self.id = None
        self._schema = schema
        self._model = model
        self._changed_items = {}
        self._autosave = False
        self._readonly = False
        self.acl_id = None
        self._acl = None
        self._load_from_data(data=data)

    @property
    def _capnp_schema(self):
        return self._schema._capnp_schema

    def _load_from_data(self, data=None):

        if self._readonly:
            raise RuntimeError("cannot load from data, obj is readonly.\n%s" % self)

        if isinstance(data,bytes):
            self._cobj_ = self._capnp_schema.from_bytes_packed(data)
            set_default = False
        else:
            self._cobj_ = self._capnp_schema.new_message()
            set_default = True
            self.acl_id = 0
            self._acl = None

        self._reset()

        if set_default:
            self._defaults_set()  # only do when new message

        if isinstance(data,bytes):
            return

        if data is not None:
            if isinstance(data,str):
                data = j.data.serializers.json.loads(data)
            if isinstance(data, dict):
                self._data_update(data=data)
            else:
                raise j.exceptions.Input("_load_from_data when string needs to be dict or json")

    def Edit(self):
        e = j.data.dict_editor.get(self._ddict)
        e.edit()
        self.data_update(e._dict)

    def _view(self):
        e = j.data.dict_editor.get(self._ddict)
        e.view()

    def _data_update(self, data=None):
        """
        upload data
        :param data:
        :return:
        """

        if data is None:
            data = {}

        if self._readonly:
            raise RuntimeError("cannot load from data, obj is readonly.\n%s" % self)

        if j.data.types.json.check(data):
            data = j.data.serializers.json.loads(data)

        if not j.data.types.dict.check(data):
            raise RuntimeError("data needs to be of type dict, now:%s" % data)

        if data != None and data != {}:
            if self._model is not None:
                data = self._model._dict_process_in(data)
            for key, val in data.items():
                setattr(self, key, val)

    @property
    def acl(self):
        if self._acl is None:
            if self.acl_id ==0:
                self._acl = self._model.bcdb.acl.new()
        return self._acl

    def _hr_get(self, exclude=[]):
        """
        human readable test format
        """
        out = "\n"
        res = self._ddict_hr_get(exclude=exclude)
        keys = [name for name in res.keys()]
        keys.sort()
        for key in keys:
            item = res[key]
            out += "- %-30s: %s\n" % (key, item)
        return out

    def save(self):
        if self._model:
            if self._readonly:
                raise RuntimeError("object readonly, cannot be saved.\n%s" % self)
            # print (self._model.__class__.__name__)
            if not self._model.__class__._name=="acl" and self.acl is not None:
                if self.acl.id is None:
                    self.acl.save()
                if self.acl.id != self.acl_id:
                    self._changed_items["ACL"]=True


            if self._changed:

                for prop_u in self._model.schema.properties_unique:
                    #find which properites need to be unique
                    #unique properties have to be indexed
                    args_search={prop_u.name:str(getattr(self,prop_u.name))}
                    r = self._model.get_from_keys(**args_search)
                    if len(r)>0:
                        j.shell()
                        w

                o = self._model._set(self)
                self.id = o.id
                # self._log_debug("MODEL CHANGED, SAVE DONE")

                return o

            return self
        raise RuntimeError("cannot save, model not known")

    def delete(self):
        if self._model:
            if self._readonly:
                raise RuntimeError("object readonly, cannot be saved.\n%s" % self)
            if not self._model.__class__.__name__ == "ACL":
                self._model.delete(self)
            return self

        raise RuntimeError("cannot save, model not known")

    def _check(self):
        self._ddict
        return True

    @property
    def _data(self):
        self._cobj #leave, is to make sure we have error if something happens
        try:
            self._cobj.clear_write_flag()
            data =  self._cobj.to_bytes_packed()
        except Exception as e:
            #need to catch exception much better (more narrow)
            self._cobj_ = self._cobj.as_builder()
            data = self._cobj_.to_bytes_packed()
        version = 1
        data2= version.to_bytes(1,'little')+bytes(bytearray.fromhex(self._schema._md5))+data
        return data2


    @property
    def _ddict_hr(self):
        """
        human readable dict
        """
        d = self._ddict_hr_get()
        return d

    @property
    def _ddict_json_hr(self):
        """
        json readable dict
        """
        return j.data.serializers.json.dumps(self._ddict_hr)

    @property
    def _json(self):
        # TODO: fix when use self._ddict
        return j.data.serializers.json.dumps(self._ddict_hr)

    @property
    def _toml(self):
        return j.data.serializers.toml.dumps(self._ddict)

    @property
    def _msgpack(self):
        return j.data.serializers.msgpack.dumps(self._ddict)

    def _str(self):
        out = "## "
        out += "{BLUE}%s{RESET}\n" % self._schema.url
        out += "{GRAY}id: %s{RESET} " % self.id
        if hasattr(self, "name"):
            out += "{RED}name:'%s'{RESET} " % self.name
        out += self._hr_get()

        return out

    def __eq__(self, val):
        if not isinstance(val, DataObjBase):
            tt = j.data.types.get("obj", self._schema.url)
            val = tt.clean(val)
        return self._data == val._data

    def __str__(self):
        return j.data.serializers.toml.dumps(self._ddict_hr)
        # out = self._str()
        #
        # out += "{RESET}\n\n"
        # out = j.core.tools.text_replace(out)
        # # #TODO: *1 when returning the text it does not represent propertly, needs to be in kosmos shell I think
        # #IS UGLY WORKAROUND
        # print(out)
        # return ""

    __repr__ = __str__
