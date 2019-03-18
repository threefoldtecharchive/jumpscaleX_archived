from Jumpscale import j
from Jumpscale.data.schema.DataObjBase import DataObjBase


class ModelOBJ(DataObjBase):

    __slots__ = ["id","_schema","_model","_autosave","_readonly","_JSOBJ","_cobj_","_changed_items","_acl_id","_acl",
                        {% for prop in obj.lists %}"_{{prop.name}}",{% endfor %}]

    def _defaults_set(self):
        pass
        {% for prop in obj.properties %}
        {% if not prop.jumpscaletype.NAME == "jsobject" %}
        if {{prop.default_as_python_code}} not in [None,"","0.0",0,'0']:
            self.{{prop.name}} = {{prop.default_as_python_code}}
        {% endif %}
        {% endfor %}

    def _reset(self):
        """
        reset all values to their default
        :return:
        """
        self._changed_items = {}
        #LIST

        {% for ll in obj.lists %}
        # self._{{ll.name}} = j.data.types.get("l",self._schema.property_{{ll.name}}.js_typelocation)
        raise RuntimeError("not get here")

        self._{{ll.name}} = {{ll.js_typelocation}}.default_get()

        for capnpbin in self._cobj_.{{ll.name_camel}}:
            self._{{ll.name}}.new(data=capnpbin)
        {% endfor %}

        #PROP
        {% for prop in obj.properties %}
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        self._schema_{{prop.name}} = j.data.schema.get(url="{{prop.jumpscaletype._schema_url}}")
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
            return {{prop.js_typelocation}}.clean(self._cobj_.{{prop.name_camel}})
        {% endif %} 
        
    @{{prop.name}}.setter
    def {{prop.name}}(self,val):
        if self._readonly:
            raise RuntimeError("object readonly, cannot set.\n%s"%self)
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        self._changed_items["{{prop.name}}"] = val
        {% else %} 
        #will make sure that the input args are put in right format
        val = {{prop.js_typelocation}}.clean(val)  #is important because needs to come in right format e.g. binary for numeric
        if True or val != self.{{prop.name}}: #TODO: shortcut for now
            self._changed_items["{{prop.name}}"] = val
            if self._model:
                # self._log_debug("change:{{prop.name}} %s"%(val))
                self._model.triggers_call(obj=self, action="change", propertyname="{{prop.name}}")
            if self._autosave:
                self.save()
        {% endif %}

    {% if prop.jumpscaletype.NAME == "numeric" %}
    @property
    def {{prop.name}}_usd(self):
        return {{prop.js_typelocation}}.bytes2cur(self.{{prop.name}}._data)

    @property
    def {{prop.name}}_eur(self):
        return {{prop.js_typelocation}}.bytes2cur(self.{{prop.name}}._data,curcode="eur")

    def {{prop.name}}_cur(self,curcode):
        """
        @PARAM curcode e.g. usd, eur, egp, ...
        """
        return {{prop.js_typelocation}}.bytes2cur(self.{{prop.name}}._data, curcode = curcode)

    {% endif %}

    {% endfor %}

    {#generate the properties for lists#}
    {% for ll in obj.lists %}
    @property
    def {{ll.name}}(self):
        return self._{{ll.name}}

    @{{ll.name}}.setter
    def {{ll.name}}(self,val):
        if self._readonly:
            raise RuntimeError("object readonly, cannot set.\n%s"%self)
        self._{{ll.name}}._inner_list=[]
        if j.data.types.string.check(val):
            val = [i.strip() for i in val.split(",")]
        for item in val:
            self._{{ll.name}}.append(item)
        if self._autosave:
            self.save()
    {% endfor %}


    @property
    def _changed(self):
        if  self._changed_items != {}:
            return True
        {% for ll in obj.lists %}
        if self._{{ll.name}}._changed:
            return True
        {% endfor %}
        return False

    @property
    def _cobj(self):
        if self._changed is False:
            return self._cobj_

        ddict = self._cobj_.to_dict()

        {% for prop in obj.lists %}
        if self._{{prop.name}}._changed:
            raise RuntimeError("should not get here")
            # #means the list was modified
            # if "{{prop.name_camel}}" in ddict:
            #     ddict.pop("{{prop.name_camel}}")
            # ddict["{{prop.name_camel}}"]=[] #make sure we have empty list
            #
            # for item in self._{{prop.name}}._inner_list:
            #     if self._{{prop.name}}._child_type.NAME is "jsobject":
            #         #use data in stead of rich object
            #         item = item._data
            #     elif hasattr(item,"_data"):
            #         item = item._data
            #     ddict["{{prop.name_camel}}"].append(item)
        {% endfor %}

        {% for prop in obj.properties %}
        #convert jsobjects to capnpbin data
        if "{{prop.name}}" in self._changed_items:
            {% if prop.jumpscaletype.NAME == "jsobject" %}
            ddict["{{prop.name_camel}}"] = self._changed_items["{{prop.name}}"]._data
            {% else %}
            # o =  {{prop.js_typelocation}}.clean(self._changed_items["{{prop.name}}"])
            o =  {{prop.js_typelocation}}.toData(self._changed_items["{{prop.name}}"])
            # if hasattr(o,"_data"):
            #     o=o._data
            ddict["{{prop.name_camel}}"] = o
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
            msg+=j.core.text.indent(str(self._schema._capnp_schema),4)+"\n"
            msg+="error was:\n%s\n"%e
            raise RuntimeError(msg)

        self._reset()

        return self._cobj_


    @property
    def _ddict(self):
        d={}
        # from pudb import set_trace; set_trace()
        {% for prop in obj.properties %}
        {% if prop.jumpscaletype.NAME == "jsobject" %} #NEED TO CHECK : #TODO: despiegk
        raise RuntimeError("not here")
        # d["{{prop.name}}"] = self.{{prop.name}}._ddict
        {% elif prop.jumpscaletype.BASETYPE == "OBJ" %}
        raise RuntimeError("not here")
        # d["{{prop.name}}"] = self.{{prop.name}}._dictdata
        {% else %}
        if isinstance(self.{{prop.name}},j.data.types._TypeBaseObjClass):
            d["{{prop.name}}"] = self.{{prop.name}}._dictdata
        else:
            d["{{prop.name}}"] = self.{{prop.name}}
        {% endif %}    
        {% endfor %}

        {% for prop in obj.lists %}
        raise RuntimeError("not here")
        # d["{{prop.name}}"] = self._{{prop.name}}.pylist()
        {% endfor %}

        if self.id is not None:
            d["id"]=self.id

        if self._model is not None:
            d=self._model._dict_process_out(d)
        return d



    def _ddict_hr_get(self,exclude=[],maxsize=100):
        """
        human readable dict
        """
        d = {}
        {% for prop in obj.properties %}
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        # d["{{prop.name}}"] = j.data.serializers.yaml.dumps(self.{{prop.name}}._ddict_hr)
        d["{{prop.name}}"] = "\n"+j.core.text.indent(self.{{prop.name}}._str(),4)
        {% else %}
        res = {{prop.js_typelocation}}.toHR(self.{{prop.name}})
        if len(str(res))<maxsize:
            d["{{prop.name}}"] = res
        {% endif %}
        {% endfor %}
        {% for prop in obj.lists %}
        d["{{prop.name}}"] = self._{{prop.name}}.pylist(subobj_format="H")
        {% endfor %}
        if self.id is not None:
            d["id"] = self.id
        for item in exclude:
            if item in d:
                d.pop(item)
        if self._model is not None:
            d=self._model._dict_process_out(d)
        return d

