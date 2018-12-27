from Jumpscale import j

List0 = j.data.schema.list_base_class_get()

class ModelOBJ():
    
    def __init__(self,schema,data=None, capnpbin=None, model=None):

        if data is None:
            data = {}
        self._schema = schema
        self._capnp_schema = schema._capnp_schema
        self.model = model
        self.autosave = False
        self.readonly = False
        self._JSOBJ = True
        self._load_from_data(data=data, capnpbin=capnpbin, keepid=False, keepacl=False)

    def _load_from_data(self,data=None, capnpbin=None, keepid=True, keepacl=True):

        if self.readonly:
            raise RuntimeError("cannot load from data, obj is readonly.\n%s"%self)

        if capnpbin is not None:
            self._cobj_ = self._capnp_schema.from_bytes_packed(capnpbin)
            set_default = False
        else:
            self._cobj_ = self._capnp_schema.new_message()
            set_default = True

        self._reset()

        if set_default:
            #should only be done when not capnpbin
            self._defaults_set()

        if not keepid:
            #means we are overwriting id, need to remove from cache
            if self.model is not None and self.model.obj_cache is not None:
                if self.id in self.model.obj_cache:
                    self.model.obj_cache.pop(self.id)
            self.id = None

        if not keepacl:
            self.acl_id = 0
            self._acl = None

        if data is not None:
            self.data_update(data=data)

    def data_update(self,data=None):
        """
        upload data
        :param data:
        :return:
        """

        if data is None:
            data={}


        if self.readonly:
            raise RuntimeError("cannot load from data, obj is readonly.\n%s"%self)

        if j.data.types.json.check(data):
            data = j.data.serializers.json.loads(data)

        if not j.data.types.dict.check(data):
            raise RuntimeError("data needs to be of type dict, now:%s"%data)

        if data!=None and data!={}:
            if self.model is not None:
                data = self.model._dict_process_in(data)
            for key,val in data.items():
                setattr(self, key, val)

    @property
    def acl(self):
        if self._acl is None:
            if self.acl_id ==0:
                self._acl = self.model.bcdb.acl.new()
        return self._acl

    def _hr_get(self,exclude=[]):
        """
        human readable test format
        """
        out = "\n"
        res = self._ddict_hr_get(exclude=exclude)
        for key, item in res.items():
            out += "%-20s: %s\n" % (key, item)
        return out


    def _defaults_set(self):
        pass
        {% for prop in obj.properties %}
        {% if not prop.jumpscaletype.NAME == "jsobject" %}
        if {{prop.default_as_python_code}} is not None:
            self.{{prop.name}} = {{prop.default_as_python_code}}
        {% endif %}
        {% endfor %}

    def _reset(self):
        """
        reset all values to their default
        :return:
        """
        self._changed_items = {}
        {% for ll in obj.lists %}
        self._{{ll.name}} = List0(self._schema.property_{{ll.name}})
        for capnpbin in self._cobj_.{{ll.name_camel}}:
            self._{{ll.name}}.new(data=capnpbin)
        {% endfor %}
        {% for prop in obj.properties %}
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        self._schema_{{prop.name}} = j.data.schema.get(url="{{prop.jumpscaletype.SUBTYPE}}")

        if self._cobj_.{{prop.name_camel}}:
            self._changed_items["{{prop.name}}"] = self._schema_{{prop.name}}.get(capnpbin=self._cobj_.{{prop.name_camel}})
        else:
            self._changed_items["{{prop.name}}"] = self._schema_{{prop.name}}.new()
        {% endif %}
        {% endfor %}


    {# generate the properties #}
    {% for prop in obj.properties %}
    @property 
    def {{prop.name}}(self):
        {% if prop.comment != "" %}
        '''
        {{prop.comment}}
        '''
        {% endif %} 
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        return self._changed_items["{{prop.name}}"]
        {% else %} 
        if "{{prop.name}}" in self._changed_items:
            return self._changed_items["{{prop.name}}"]
        else:
            return self._cobj_.{{prop.name_camel}}
        {% endif %} 
        
    @{{prop.name}}.setter
    def {{prop.name}}(self,val):
        if self.readonly:
            raise RuntimeError("object readonly, cannot set.\n%s"%self)
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        self._changed_items["{{prop.name}}"] = val
        {% else %} 
        #will make sure that the input args are put in right format
        val = {{prop.js_typelocation}}.clean(val)  #is important because needs to come in right format e.g. binary for numeric
        if self.{{prop.name}} != val:
            self._changed_items["{{prop.name}}"] = val
            if self.autosave:
                self.save()
        {% endif %}

    {% if prop.jumpscaletype.NAME == "numeric" %}
    @property
    def {{prop.name}}_usd(self):
        return {{prop.js_typelocation}}.bytes2cur(self.{{prop.name}})

    @property
    def {{prop.name}}_eur(self):
        return {{prop.js_typelocation}}.bytes2cur(self.{{prop.name}},curcode="eur")

    def {{prop.name}}_cur(self,curcode):
        """
        @PARAM curcode e.g. usd, eur, egp, ...
        """
        return {{prop.js_typelocation}}.bytes2cur(self.{{prop.name}}, curcode = curcode)

    {% endif %}

    {% endfor %}

    {#generate the properties for lists#}
    {% for ll in obj.lists %}
    @property
    def {{ll.name}}(self):
        return self._{{ll.name}}

    @{{ll.name}}.setter
    def {{ll.name}}(self,val):
        if self.readonly:
            raise RuntimeError("object readonly, cannot set.\n%s"%self)
        self._{{ll.name}}._inner_list=[]
        if j.data.types.string.check(val):
            val = [i.strip() for i in val.split(",")]
        for item in val:
            self._{{ll.name}}.append(item)
        if self.autosave:
            self.save()
    {% endfor %}


    def save(self):
        if self.model:
            if self.readonly:
                raise RuntimeError("object readonly, cannot be saved.\n%s"%self)
            if not self.model.__class__.__name__=="ACL" and self.acl is not None:
                if self.acl.id is None:
                    self.acl.save()
                if self.acl.id != self.acl_id:
                    self._changed_items["ACL"]=True

            if self._changed:
                o=self.model._set(self)
                self.id = o.id
                # self._logger.debug("MODEL CHANGED, SAVE DONE")
                return o

            return self
        raise RuntimeError("cannot save, model not known")

    def delete(self):
        if self.model:
            if self.readonly:
                raise RuntimeError("object readonly, cannot be saved.\n%s"%self)
            if not self.model.__class__.__name__=="ACL":
                self.model.delete(self)
            return self
        raise RuntimeError("cannot save, model not known")

    def _check(self):
        self._ddict
        return True

    @property
    def _changed(self):
        if  self._changed_items != {}:
            return True
        {% for ll in obj.lists %}
        if self._{{ll.name}}.changed:
            return True
        {% endfor %}
        return False

    @property
    def _cobj(self):
        if self._changed is False:
            return self._cobj_

        ddict = self._cobj_.to_dict()

        {% for prop in obj.lists %}
        if self._{{prop.name}}.changed:
            #means the list was modified
            if "{{prop.name_camel}}" in ddict:
                ddict.pop("{{prop.name_camel}}")
            ddict["{{prop.name_camel}}"]=[]
            for item in self._{{prop.name}}._inner_list:
                if self._{{prop.name}}.schema_property.pointer_type is not None:
                    #use data in stead of rich object
                    item = item._data
                ddict["{{prop.name_camel}}"].append(item)
        {% endfor %}

        {% for prop in obj.properties %}
        #convert jsobjects to capnpbin data
        if "{{prop.name}}" in self._changed_items:
            {% if prop.jumpscaletype.NAME == "jsobject" %}
            ddict["{{prop.name_camel}}"] = self._changed_items["{{prop.name}}"]._data
            {% else %}
            ddict["{{prop.name_camel}}"] = {{prop.js_typelocation}}.toData(self._changed_items["{{prop.name}}"])
            {% endif %}
        {% endfor %}


        try:
            self._cobj_ = self._capnp_schema.new_message(**ddict)
        except Exception as e:
            msg="\nERROR: could not create capnp message\n"
            try:
                msg+=j.core.text.indent(j.data.serializers.json.dumps(ddict,sort_keys=True,indent=True),4)+"\n"
            except:
                msg+=j.core.text.indent(str(ddict),4)+"\n"
            msg+="schema:\n"
            msg+=j.core.text.indent(str(self._schema.capnp_schema),4)+"\n"
            msg+="error was:\n%s\n"%e
            raise RuntimeError(msg)

        self._reset()

        return self._cobj_

    @property
    def _data(self):        
        try:
            self._cobj_.clear_write_flag()
            return self._cobj.to_bytes_packed()
        except:
            self._cobj_=self._cobj_.as_builder()
            return self._cobj.to_bytes_packed()

    @property
    def _ddict(self):
        d={}
        {% for prop in obj.properties %}
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        d["{{prop.name}}"] = self.{{prop.name}}._ddict
        {% else %}
        d["{{prop.name}}"] = self.{{prop.name}}
        {% endif %}    
        {% endfor %}

        {% for prop in obj.lists %}
        d["{{prop.name}}"] = self._{{prop.name}}.pylist()
        {% endfor %}
        if self.id is not None:
            d["id"]=self.id

        if self.model is not None:
            d=self.model._dict_process_out(d)
        return d

    @property
    def _ddict_hr(self):
        """
        human readable dict
        """
        d={}
        {% for prop in obj.properties %}
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        d["{{prop.name}}"] = self.{{prop.name}}._ddict_hr
        {% else %}
        d["{{prop.name}}"] = {{prop.js_typelocation}}.toHR(self.{{prop.name}})
        {% endif %}
        {% endfor %}
        {% for prop in obj.lists %}
        d["{{prop.name}}"] = self._{{prop.name}}.pylist(subobj_format="H")
        {% endfor %}
        if self.id is not None:
            d["id"]=self.id
        if self.model is not None:
            d=self.model._dict_process_out(d)
        return d

    @property
    def _ddict_json_hr(self):
        """
        json readable dict
        """
        # d={}
        # {% for prop in obj.properties %}
        # {% if prop.jumpscaletype.NAME == "jsobject" %}
        # d["{{prop.name}}"] = self.{{prop.name}}._ddict_json
        # {% else %}
        # d["{{prop.name}}"] = {{prop.js_typelocation}}.toJSON(self.{{prop.name}})
        # {% endif %}
        # {% endfor %}
        # {% for prop in obj.lists %}
        # d["{{prop.name}}"] = self._{{prop.name}}.pylist(subobj_format="J")
        # {% endfor %}
        # if self.id is not None:
        #     d["id"]=self.id
        # if self.model is not None:
        #     d=self.model._dict_process_out(d)
        # return d
        return j.data.serializers.json.dumps(self._ddict_hr)

    def _ddict_hr_get(self,exclude=[],maxsize=100):
        """
        human readable dict
        """
        d = {}
        {% for prop in obj.properties %}
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        d["{{prop.name}}"] = self.{{prop.name}}._ddict_hr
        {% else %}
        res = {{prop.js_typelocation}}.toHR(self.{{prop.name}})
        if len(str(res))<maxsize:
            d["{{prop.name}}"] = res
        {% endif %}
        {% endfor %}
        if self.id is not None:
            d["id"] = self.id
        for item in exclude:
            if item in d:
                d.pop(item)
        return d



    @property
    def _json(self):
        return j.data.serializers.json.dumps(self._ddict,True,True)

    @property
    def _toml(self):
        return j.data.serializers.toml.dumps(self._ddict)

    @property
    def _msgpack(self):
        return j.data.serializers.msgpack.dumps(self._ddict)

    def __str__(self):
        return j.data.serializers.json.dumps(self._ddict_hr,sort_keys=True, indent=True)

    __repr__ = __str__
