from Jumpscale import j


class DataObjBase():

    def __init__(self,schema, data={}, capnpbin=None, model=None):
        # if data is None:
        #     data = {}
        self._cobj_ = None
        self.id = None
        self._schema = schema
        self._model = model
        self._changed_items = []
        self._autosave = False
        self._readonly = False
        self._JSOBJ = True
        self._load_from_data(data=data, capnpbin=capnpbin, keepid=False, keepacl=False)



    @property
    def _capnp_schema(self):
        return self._schema._capnp_schema


    def _load_from_data(self,data=None, capnpbin=None, keepid=True, keepacl=True):

        if self._readonly:
            raise RuntimeError("cannot load from data, obj is readonly.\n%s"%self)

        if capnpbin is not None:
            self._cobj_ = self._capnp_schema.from_bytes_packed(capnpbin)
            set_default = False
        else:
            self._cobj_ = self._capnp_schema.new_message()
            set_default = True

        self._reset()

        if set_default:
            self._defaults_set() #only do when new message

        if not keepid:
            #means we are overwriting id, need to remove from cache
            if self._model is not None and self._model.obj_cache is not None:
                if self.id is not None and self.id in self._model.obj_cache:
                    self._model.obj_cache.pop(self.id)

        # if not keepacl:
        #     self.acl_id = 0
        #     self._acl = None

        if data is not None:
            if j.data.types.string.check(data):
                data = j.data.serializers.json.loads(data)
            if not isinstance(data,dict):
                raise j.exceptions.Input("_load_from_data when string needs to be dict as json")
            self._data_update(data=data)

    def Edit(self):
        e = j.data.dict_editor.get(self._ddict)
        e.edit()
        self.data_update(e._dict)

    def _view(self):
        e = j.data.dict_editor.get(self._ddict)
        e.view()

    def _data_update(self,data=None):
        """
        upload data
        :param data:
        :return:
        """

        if data is None:
            data={}


        if self._readonly:
            raise RuntimeError("cannot load from data, obj is readonly.\n%s"%self)

        if j.data.types.json.check(data):
            data = j.data.serializers.json.loads(data)

        if not j.data.types.dict.check(data):
            raise RuntimeError("data needs to be of type dict, now:%s"%data)

        if data!=None and data!={}:
            if self._model is not None:
                data = self._model._dict_process_in(data)
            for key,val in data.items():
                setattr(self, key, val)

    # @property
    # def acl(self):
    #     if self._acl is None:
    #         if self.acl_id ==0:
    #             self._acl = self._model.bcdb.acl.new()
    #     return self._acl

    def _hr_get(self,exclude=[]):
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


    def Save(self):
        if self._model:
            if self._readonly:
                raise RuntimeError("object readonly, cannot be saved.\n%s"%self)
            # print (self._model.__class__.__name__)
            # if not self._model.__class__._name=="acl" and self.acl is not None:
            #     if self.acl.id is None:
            #         self.acl.save()
            #     if self.acl.id != self.acl_id:
            #         self._changed_items["ACL"]=True

            if self._changed:
                o=self._model._set(self)
                self.id = o.id
                # self._log_debug("MODEL CHANGED, SAVE DONE")
                return o

            return self
        raise RuntimeError("cannot save, model not known")

    def Delete(self):
        if self._model:
            if self._readonly:
                raise RuntimeError("object readonly, cannot be saved.\n%s"%self)
            if not self._model.__class__.__name__=="ACL":
                self._model.delete(self)
            return self
        raise RuntimeError("cannot save, model not known")

    def _check(self):
        self._ddict
        return True


    @property
    def _data(self):
        try:
            self._cobj.clear_write_flag()
            return self._cobj.to_bytes_packed()
        except:
            self._cobj_=self._cobj.as_builder()
            return self._cobj_.to_bytes_packed()


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
        return j.data.serializers.json.dumps(str(self._ddict),True,True)

    @property
    def _toml(self):
        return j.data.serializers.toml.dumps(self._ddict)


    @property
    def _msgpack(self):
        return j.data.serializers.msgpack.dumps(self._ddict)

    def _str(self):
        out = "## "
        out += "{BLUE}%s{RESET}\n"%self._schema.url
        out += "{GRAY}id: %s{RESET} " %self.id
        if hasattr(self,"name"):
            out += "{RED}name:'%s'{RESET} "%self.name
        out += self._hr_get()

        return out

    def __eq__(self, val):
        if not isinstance(val,DataObjBase):
            tt = j.data.types.get("obj",self._schema.url)
            val = tt.clean(val)
        return self._data == val._data

    def __str__(self):
        out = self._str()

        out += "{RESET}\n\n"
        out = j.core.tools.text_replace(out)
        # #TODO: *1 when returning the text it does not represent propertly, needs to be in kosmos shell I think
        #IS UGLY WORKAROUND
        print(out)
        return ""

    __repr__ = __str__
