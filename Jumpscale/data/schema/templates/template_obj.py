from Jumpscale import j

from capnp import KjException

class ModelOBJ(j.data.schema._JSXObjectClass):

    # __slots__ = ["id","_schema","_model","_autosave","_JSOBJ","_cobj_","_changed_items","_acl_id","_acl",
    #                     {% for prop in obj.properties %}"_{{prop.name}}",{% endfor %}]

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
        :return:
        """
        self._changed_items = {}
        #PROP
        {% for prop in obj.properties %}
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        self._schema_{{prop.name}} = j.data.schema.get_from_md5(md5="{{prop.jumpscaletype._schema_md5}}")
        if self._cobj_.{{prop.name_camel}}:
            data = self._cobj_.{{prop.name_camel}}
            self._changed_items["{{prop.name}}"] = self._schema_{{prop.name}}.get(data=data)
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
            v = {{prop.js_typelocation}}.clean(self._cobj_.{{prop.name_camel}})
            if isinstance(v,j.data.types._TypeBaseObjClass):
                self._changed_items["{{prop.name}}"] = v
            return v

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
        if val != self.{{prop.name}}:
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


    @property
    def _changed(self):
        if  self._changed_items != {}:
            return True
        return False

    @property
    def _cobj(self):
        if self._changed is False:
            return self._cobj_

        ddict = self._cobj_.to_dict()

        {% for prop in obj.properties %}
        #convert jsobjects to data data
        if "{{prop.name}}" in self._changed_items:
            {% if prop.has_jsxobject %}
            data =  {{prop.js_typelocation}}.toData(self._changed_items["{{prop.name}}"],model=self._model)
            {% else %}
            data =  {{prop.js_typelocation}}.toData(self._changed_items["{{prop.name}}"])
            {% endif %}

            ddict["{{prop.name_camel}}"] = data
        {% endfor %}


        try:
            self._cobj_ = self._capnp_schema.new_message(**ddict)
        except KjException as e:
            msg="\nERROR: could not create capnp message\n"
            j.shell()
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

        {% for prop in obj.properties %}
        # prop.name: {{prop.name}}
        # prop.jumpscaletype.NAME: {{prop.jumpscaletype.NAME}}
        # prop.jumpscaletype.BASETYPE: {{prop.jumpscaletype.BASETYPE}}
        {% endfor %}

        {% for prop in obj.properties %}
        {% if prop.jumpscaletype.NAME == "jsobject" %}
        d["{{prop.name}}"] = self.{{prop.name}}._ddict
        {% else %}
        if isinstance(self.{{prop.name}},j.data.types._TypeBaseObjClass):
            d["{{prop.name}}"] = self.{{prop.name}}._dictdata
        else:
            d["{{prop.name}}"] = self.{{prop.name}}
        {% endif %}
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
        if {{prop.js_typelocation}}.NAME in ["list"]:
            res = {{prop.js_typelocation}}.toHR(self.{{prop.name}})
        else:
            res = {{prop.js_typelocation}}.toHR(self.{{prop.name}})
            # if len(str(res))<maxsize:
            #     res = "\n"+j.core.text.indent(res,4)
        d["{{prop.name}}"] = res
        # if len(str(res))<maxsize:
        #     d["{{prop.name}}"] = res
        # else:
        #     d["{{prop.name}}"] = "\n"+j.core.text.indent(res,4)
        {% endif %}
        {% endfor %}
        if self.id is not None:
            d["id"] = self.id
        for item in exclude:
            if item in d:
                d.pop(item)
        if self._model is not None:
            d=self._model._dict_process_out(d)
        return d

