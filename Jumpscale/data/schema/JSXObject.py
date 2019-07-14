from Jumpscale import j


class JSXObject(j.application.JSBaseClass):
    def _init_pre(self, capnpdata=None, datadict={}, schema=None, model=None):
        self._capnp_obj_ = None
        self.id = None
        assert schema
        self._schema = schema
        self._model = model
        if model:
            assert self._schema == self._model.schema  # they need to be the same

        self._deserialized_items = {}

        self._autosave = False
        self.acl_id = None
        self._acl = None

        self._load_from_data(capnpdata=capnpdata)  # ONLY LOADS THE self._capnp_obj_
        if datadict:
            self._data_update(datadict)

        # self.nid = 1

        self._logger_enable()

    @property
    def _key(self):
        if hasattr(self, "id") and self.id:
            return "%s:%s" % (self._schema.url, self.id)
        else:
            return self._schema.url

    @property
    def _readonly(self):
        if self._model:
            return self._model.readonly
        return False

    @property
    def _capnp_schema(self):
        return self._schema._capnp_schema

    def _data_update(self, datadict):
        if not isinstance(datadict, dict):
            raise RuntimeError("need to be dict, was:\n%s" % datadict)
        if self._model is not None:
            data = self._model._dict_process_in(datadict)
        for key, val in datadict.items():
            try:
                setattr(self, key, val)
            except Exception as e:
                if isinstance(e, ValueError):
                    msg = "cannot update data for: %s  set prop %s with '%s'" % (self._schema.url, key, val)
                    e.args = (msg,)
                raise e

    def _load_from_data(self, capnpdata=None):
        """
        THIS ERASES EXISTING DATA !!!

        :param data: can be binary (capnp), str=json, or dict
        :return:
        """

        if self._model is not None and self._readonly:
            raise RuntimeError("cannot load from data, model stor for obj is readonly.\n%s" % self)
        if self._readonly:
            raise RuntimeError("cannot load from data, readonly.\n%s" % self)

        if isinstance(capnpdata, bytes):
            self._capnp_obj_ = self._capnp_schema.from_bytes_packed(capnpdata)
            set_default = False
        else:
            self._capnp_obj_ = self._capnp_schema.new_message()
            set_default = True
            self.acl_id = 0
            self._acl = None

        if set_default:
            self._defaults_set()  # only do when new message

    def Edit(self):
        e = j.data.dict_editor.get(self._ddict)
        e.edit()
        self._load_from_data(e._dict)

    def _view(self):
        e = j.data.dict_editor.get(self._ddict)
        e.view()

    @property
    def acl(self):
        if self._acl is None:
            if self.acl_id == 0:
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

    def save(self, serialize=False):
        if self._changed:
            self._capnp_obj  # makes sure we get back to binary form
            if serialize:
                self._deserialized_items = {}  # need to go back to smallest form
        if self._model:
            if self._readonly:
                raise RuntimeError("object readonly, cannot be saved.\n%s" % self)
            # print (self._model.__class__.__name__)
            if not self._model.__class__._name == "acl" and self._acl is not None:
                if self.acl.id is None:
                    self.acl.save()
                if self.acl.id != self.acl_id:
                    self._deserialized_items["ACL"] = True

            if self._changed:

                for prop_u in self._model.schema.properties_unique:
                    # find which properties need to be unique
                    # unique properties have to be indexed
                    args_search = {prop_u.name: getattr(self, prop_u.name)}
                    r = self._model.find(**args_search)
                    msg = "could not save, was not unique.\n%s.\nfound:\n%s" % (args_search, r)
                    if len(r) > 1:
                        # can for sure not be ok
                        raise j.exceptions.Input(msg)
                    elif len(r) == 1:
                        if self.id:
                            if not self.id == r[0].id:
                                # j.shell()
                                raise j.exceptions.Input(msg)
                        else:
                            self.id = r[0].id
                            self._ddict_hr  # to trigger right serialization
                            if self._data == r[0]._data:
                                assert self._model.sid == r[0]._model.sid
                                return self  # means data was not changed

                o = self._model.set(self)
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
        self._capnp_obj  # leave, is to make sure we have error if something happens
        return j.data.serializers.jsxdata.dumps(self, model=self._model)

    @property
    def _ddict_hr(self):
        """
        human readable dict
        """
        d = self._ddict_hr_get(ansi=False)
        return d

    @property
    def _ddict_json_hr(self):
        """
        json readable dict
        """
        return j.data.serializers.json.dumps(self._ddict_hr)

    @property
    def _json(self):
        return j.data.serializers.json.dumps(self._ddict)  # DO NOT USE THE HR ONE

    @property
    def _toml(self):
        return j.data.serializers.toml.dumps(self._ddict)

    @property
    def _msgpack(self):
        return j.data.serializers.msgpack.dumps(self._ddict)

    def __eq__(self, val):
        if not isinstance(val, JSXObject):
            tt = j.data.types.get("jsxobject", self._schema.url)
            val = tt.clean(val)
        return self._data == val._data

    def __str__(self):
        out = self._str_get(ansi=True)
        out = out.replace("\n\n\n", "\n\n").replace("\n\n\n", "\n\n")
        # #TODO: *1 when returning the text it does not represent propertly, needs to be in kosmos shell I think
        # IS UGLY WORKAROUND
        print(out)
        return ""

    __repr__ = __str__
