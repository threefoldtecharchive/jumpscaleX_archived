from Jumpscale import j
from .JSBase import JSBase
import types


class JSBaseConfig(JSBase):

    def _class_init(self):

        if not hasattr(self.__class__,"_class_init_done"):

            if not hasattr(self.__class__,"_SCHEMATEXT"):
                raise RuntimeError("need _SCHEMATEXT as class property.\n%s"%(HELPTEXT))

            JSBase._class_init(self)


    def __init__(self,data, factory=None, **kwargs):
        """
        :param name: for the service
        :param data, if specified will be used to populate this object, is the result of querying the model
        :param factory, if there was a factory calling this init
        :param kwargs: TO PASS on to the class who inherits from this
        """
        self._class_init() #is needed to init class properties, needs to be first thing
        JSBase.__init__(self,init=False)

        self.data = data
        self._factory = factory

        self._init(**kwargs)

        if "name" not in  self.data._ddict:
            raise RuntimeError("name needs to be specified in data")

        self.key = "%s_%s"%(self.__class__.__name__,self.data.name)

        #if factory specified, add us to the children of the factory
        if self._factory:
            self._factory._children[self.key] = self


    def _obj_cache_reset(self):
        """
        puts the object back to its basic state
        :return:
        """
        JSBase._obj_cache_reset(self)
        self.__dict__["_data"] = None

    @property
    def _model(self):
        if self._factory is None:
            raise RuntimeError("cannot get model, because factory not specified in self._factory")
        return self._factory._model

    @property
    def _id(self):
        return self.data.id

    def delete(self):
        self._model.delete(self.data)
        if self._factory:
            self._factory._children.pop(self.key)

    def save(self):
        self.data.save()

    def data_update(self,**kwargs):
        """
        will not automatically save the data, don't forget to call self.save()
         
        :param kwargs:
        :return:
        """
        self.data.data_update(data=kwargs)
        # self.data.save()

    def _data_trigger_new(self):
        pass

    def _data_trigger_delete(self):
        pass

    def edit(self):
        path = j.core.tools.text_replace("{DIR_TEMP}/js_baseconfig_%s.toml"%self.__class__._location)
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
        path = j.core.tools.text_replace("{DIR_TEMP}/js_baseconfig_%s.toml"%self.__class__._location)
        data_in = self.data._toml
        j.tools.formatters.print_toml(data_in)


    def __getattr__(self, attr):
        if attr.startswith("_"):
            return self.__getattribute__(attr)
        if attr in self._model.schema.propertynames:
            return self.data.__getattribute__(attr)
        return self.__getattribute__(attr)
        # raise RuntimeError("could not find attribute:%s"%attr)

    def __dir__(self):
        r = self._model.schema.propertynames
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

        if "data" in self.__dict__ and key in self._model.schema.propertynames:
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
