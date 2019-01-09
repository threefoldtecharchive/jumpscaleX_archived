from Jumpscale import j
from .JSBase import JSBase
import types

class JSBaseConfig(JSBase):


    def __init__(self,dataobj=None,factory=None,childclass_name=None,**kwargs):
        JSBase.__init__(self,init=False)
        # if factory is None:
        #     raise RuntimeError("factory cannot be None")
        self._childclass_name = childclass_name
        self._factory = factory
        self.data = dataobj

        self._init(**kwargs)

    def _obj_cache_reset(self):
        self.__dict__["factory"] = None
        self.__dict__["data"] = None

    @property
    def _id(self):
        return self.data.id

    def save(self):
        self.data.save()

    def delete(self):
        self.data.model.delete(self.data)
        if self._factory:
            self._factory._delete(name=self.name,childclass_name=self._childclass_name)

    def data_update(self,**kwargs):
        self.data.data_update(data=kwargs)
        # self.data.save()

    def _data_trigger_new(self):
        pass

    def _data_trigger_delete(self):
        pass

    def edit(self):
        path = j.core.tools.text_replace("{DIR_TEMP}/js_baseconfig_%s.toml"%self.__location__)
        data_in = self.data._toml
        j.sal.fs.writeFile(path,data_in)
        j.core.tools.file_edit(path)
        data_out = j.sal.fs.readFile(path)
        if data_in != data_out:
            self._logger.debug("'%s' instance '%s' has been edited (changed)"%(self._factory.__jslocation__,self.data.name))
            data2 = j.data.serializers.toml.loads(data_out)
            self.data.data_update(data2)
        j.sal.fs.remove(path)

    def view(self):
        path = j.core.tools.text_replace("{DIR_TEMP}/js_baseconfig_%s.toml"%self.__location__)
        data_in = self.data._toml
        j.tools.formatters.print_toml(data_in)


    def __getattr__(self, attr):
        if attr.startswith("_"):
            return self.__getattribute__(attr)
        if attr in self._factory._model_get(self._childclass_name).schema.propertynames:
            return self.data.__getattribute__(attr)
        return self.__getattribute__(attr)
        # raise RuntimeError("could not find attribute:%s"%attr)

    def __dir__(self):
        r = self._factory._model_get(self._childclass_name).schema.propertynames
        for item in self.__dict__.keys():
            # print("-%s"%item)
            if item not in r:
                r.append(item)
        # for item in self.__class__.__dict__.keys():
        #     # if isinstance(self.__dict__[item],types.MethodType):
        #     if not item.startswith("_"):
        #         if item in r:
        #             r.pop(item)
        #         item+="("
        #         r.append(item)
        return r

    def __setattr__(self, key, value):
        if key.startswith("_") or key=="data":
            self.__dict__[key]=value
            return

        if "data" in self.__dict__ and key in self._factory._model_get(self._childclass_name).schema.propertynames:
            # if value != self.data.__getattribute__(key):
            self._logger.debug("SET:%s:%s"%(key,value))
            self.__dict__["data"].__setattr__(key,value)

        self.__dict__[key]=value


    def __str__(self):
        try:
            out = "%s\n%s\n"%(self.__class__.__name__,self.data)
        except:
            out = str(self.__class__)+"\n"
            out+=j.core.text.prefix(" - ", self.data)
        return out

    __repr__ = __str__
