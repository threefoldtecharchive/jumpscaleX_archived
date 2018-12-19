from Jumpscale import j
from .JSBase import JSBase

class JSBaseConfig(JSBase):

    _SCHEMATEXT = None
    _MODEL = None

    def __init__(self,id=None,data={},**kwargs):
        JSBase.__init__(self,init=False)

        self._id_ = id
        #lets get the schema attached to class
        if self.__class__._SCHEMATEXT is not None:
            if self.__class__._MODEL is None:
                self.__class__._MODEL = j.application.bcdb_system.model_get_from_schema(self.__class__._SCHEMATEXT)
        m=self.__class__._MODEL
        res = None

        self._logger_enable()

        if id is not None:
            res = m.get(id)
        else:
            if len(kwargs.values())>0:
                propnames = [i for i in kwargs.keys()]
                propnames_keys_in_schema = [item.name for item in m.schema.index_key_properties if item.name in propnames]

                if len(propnames_keys_in_schema)>0:
                    #we can try to find this config
                    res = m.get_from_keys(**kwargs)
                    if len(res)>1:
                        raise RuntimeError("found too many items for :%s, args:\n%s\n%s"%(self.__class__.__name__,kwargs,res))
                    elif len(res)==1:
                        res = res[0]
                        self._logger.debug("existing obj:%s"%res)
                    else:
                        res=None


        if res is None:
            self._logger.debug("new obj")
            data.update(kwargs)
            self.data = m.new(data=data)
            #does not exist yet
            self._init_new()
            self.save()
        else:
            self._isnew = False
            self.data = res

        self._init()


    @property
    def _id(self):
        return self.data.id
        # if self._id_ is None:
        #     self._id_ = self.__class__._MODEL.bcdb.name+"_%s"%self.data.id
        # return self._id_

    def save(self):
        self.data.save()

    def delete(self):
        self.data.model.delete(self.data)

    def data_update(self,**kwargs):
        self.data.load_from_data(data=kwargs,reset=False)
        self.data.save()

    def _init_new(self):
        self._isnew=True
        pass

    def __getattr__(self, attr):
        # if self.__class__._MODEL is None:
        #     return self.__getattribute__(attr)
        if attr in self.__class__._MODEL.schema.properties_list:
            return self.data.__getattribute__(attr)
        return self.__getattribute__(attr)
        # raise RuntimeError("could not find attribute:%s"%attr)

    def __dir__(self):
        r = self.__class__._MODEL.schema.properties_list
        for item in self.__dict__.keys():
            if item not in r:
                r.append(item)
        return r

    def __setattr__(self, key, value):
        if "data" in self.__dict__ and key in self.__class__._MODEL.schema.properties_list:
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
