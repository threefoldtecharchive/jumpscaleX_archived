from Jumpscale import j

from .JSBase import JSBase

METHODS=["find","get","reset","count","delete"]

class KosmosServices():

    def __init__(self,factory):
        self._factory = factory

    def _obj_cache_reset(self):
        for key,val in self.__dict__.items():
            if not key.startswith("_") and key not in ["KOSMOS","K","kosmos"]:
                self.__dict__[key]._obj_cache_reset()
                del self.__dict__[key]
                self.__dict__[key]=None

    def __getattr__(self, name):
        #if private then just return
        if name.startswith("_"):
            return self.__dict__[name]
        if name.lower().rstrip("(") in METHODS:
            return self._factory.__getattribute__(name.lower().rstrip("("))
        m = self.__dict__["_factory"]
        #else see if we can from the factory find the child object
        r =  m.get(name=name,die=False)
        #if none means does not exist yet will have to create a new one
        if r is None:
            r=m.new(name=name)

        return r

    def __dir__(self):
        #list the children from the factory
        m = self.__dict__["_factory"]
        x = [item.name for item in self._factory._children.values()]
        for item in m._get_all():
            if item.name not in x:
                x.append(item.name)
        for i in METHODS:
            x.append(i[0].upper()+i[1:].lower()+"(")
        return x

    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name]=value
            return
        raise RuntimeError("readonly")

    def __str__(self):
        out = "kosmos:%s\n"%self._factory.__jslocation__
        for ite in self.__dir__():
            out+=" - %s\n"%ite
        return out

    __repr__ = __str__


class JSFactoryBase(JSBase):

    _location = None
    _CHILDCLASS = None


    def __init__(self):
        JSBase.__init__(self)
        if "clients" in self.__location__:
            self.instances = KosmosServices(self)
        else:
            self.services = KosmosServices(self)
        self._obj_cache_reset()
        self._logger_enable()
        self._children = {}
        self._init()


    def _obj_cache_reset(self):
        """
        make sure that all objects we remember inside are emptied
        :return:
        """
        self.__models = {}
        self.__dict__["_children"] = {}
        if "clients" in self.__location__:
            self.instances._obj_cache_reset()
        else:
            self.services._obj_cache_reset()

    @property
    def name(self):
        return self.__location__.split(".")[-1]

    def new(self,name,childclass_name=None,**kwargs):
        """
        :param name: for the service
        :param kwargs: the data elements
        :param childclass_name, if different typen of childclass, specify its name, needs to be implemented in _childclass_selector
        :return: the service
        """
        data = self._model_get(childclass_name).new()
        data.name = name
        if kwargs is not {}:
            data.data_update(data=kwargs)

        child_class = self._childclass_selector(childclass_name=childclass_name, data=data)

        self._logger.debug("create child for %s: name:%s class:'%s' "%(self.__location__,name,childclass_name))

        o = child_class(factory=self,dataobj=data,childclass_name=childclass_name)

        o._data_trigger_new()
        o._isnew = True

        if childclass_name is not None:
            key = "%s_%s"%(childclass_name,name)
        else:
            key = name

        self._children[key] = o

        return self._children[key]

    def delete(self,name,childclass_name=None):
        if childclass_name is not None:
            key = "%s_%s"%(childclass_name,name)
        else:
            key = name
        o=self._children[key]
        o._data_trigger_delete()
        self._children.pop(key)


    def _childclass_selector(self,childclass_name=None, data=None):
        """
        gives a creator of a factory the ability to change the type of child to be returned

        :param data: the data is passed to this method to make it possible to decide the type of the childclass from the config
        see zdb client for an example
        :return: the child class
        """
        if self.__class__._CHILDCLASS is None:
            raise RuntimeError("__class__._CHILDCLASS should be set")
        return self.__class__._CHILDCLASS

    def get(self,name=None,id=None,die=True ,create_new=True,childclass_name=None,**kwargs):
        """
        :param id: id of the obj to find, is a unique id
        :param name: of the object, can be empty when searching based on id or the search criteria (kwargs)
        :param search criteria (if name not used) or data elements for the new one being created
        :param die, means will give error when object not found
        :param create_new, if True it will automatically create a new one
        :param childclass_name, if different typen of childclass, specify its name, needs to be implemented in _childclass_selector
        :return: the service
        """

        if name is not None:
            if childclass_name is not None:
                key = "%s_%s"%(childclass_name,name)
            else:
                key = name
            if key in self._children:
                return self._children[key]

        if id is not None:
            data = self._model_get(childclass_name).get(id=id)
            name = data.name
        else:
            if name is None:
                #need to find based on kwargs
                res = self._find_obj(childclass_name=childclass_name,**kwargs)
                if len(res)<1:
                    return self._error_input_raise("Did not find services for :%s, search criteria:\n%s"%(self.__location__,kwargs))
                elif len(res)>1:
                    return self._error_input_raise("Found more than 1 service for :%s, search criteria:\n%s"%(self.__location__,kwargs))
                data = res[0]
                name = data.name
            else:
                res = self._find_obj(childclass_name=childclass_name,name=name)
                if len(res)<1:
                    if create_new:
                        return self.new(name=name,childclass_name=childclass_name,**kwargs)
                    if die:
                        return self._error_input_raise("Did not find the service for '%s', name looking for:\n%s"%(self.__location__,name))
                    else:
                        return None
                elif len(res)>1:
                    return self._error_input_raise("Found more than 1 service for '%s', name looking for:\n%s"%(self.__location__,name))
                else:
                    data=res[0]

        if childclass_name is not None:
            key = "%s_%s"%(childclass_name,name)
        else:
            key = name
        if key in self._children:
            return self._children[key]

        child_class  = self._childclass_selector(childclass_name=childclass_name)
        o = child_class(factory=self,dataobj=data,childclass_name=childclass_name,**kwargs)
        self._children[key] = o

        return self._children[key]

    def reset(self,childclass_name=None):
        """
        will remove all the instances, be carefull
        :return:

        """
        for item in self.find(childclass_name=childclass_name):
            item.delete()

    def count(self,childclass_name=None):
        return self._count(childclass_name=childclass_name)

    @property
    def _model(self):
        return self._model_get()

    def _model_get(self,childclass_name=None):
        if childclass_name not in self.__models:
            child_class = self._childclass_selector(childclass_name=childclass_name)
            self.__models[childclass_name] = j.application.bcdb_system.model_get_from_schema(child_class._SCHEMATEXT)
        return self.__models[childclass_name]

    def _find_obj(self, childclass_name=None, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the objects
        """
        if len(kwargs)>0:
            propnames = [i for i in kwargs.keys()]
            propnames_keys_in_schema = [item.name for item in self._model_get(childclass_name=childclass_name).schema.properties_index_keys if item.name in propnames]
            if len(propnames_keys_in_schema) > 0:
                # we can try to find this config
                return self._model_get(childclass_name=childclass_name).get_from_keys(**kwargs)
            else:
                raise RuntimeError("cannot find obj with kwargs:\n%s\n in %s\nbecause kwargs do not match, is there * in schema"%(kwargs,self))
            return []
        else:
            return self._model_get(childclass_name).get_all()


    def find(self, childclass_name=None,**kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the objects
        """
        res=[]
        for dataobj in self._find_obj( childclass_name=childclass_name,**kwargs):
            res.append(self.get(dataobj.id,childclass_name=childclass_name))
        return res


    # def _load(self, klass):
    #     name = klass.__name__
    #     self.__dict__[name] = klass
    #     self.__dict__[name].coordinator = self

    # def _example_run(self, filepath="example", obj_key="main", **kwargs):
    #     """
    #     the example file will be copied to {DIR_VAR}/CODEGEN/$uniquekey and executed there
    #     template engine jinja is used to apply kwargs onto this file
    #
    #     :param filepath: name of file to execute can be e.g. example.py or example or examples/example1.py
    #                     is always relative to the file you call this function from
    #     :param kwargs: the arguments which will be given to the template engine
    #     :param obj_key: is the name of the function we will look for to execute, cannot have arguments
    #            to pass arguments to the example script, use the templating feature
    #
    #     :return: result = is the result of the method called
    #
    #     """
    #     print("##: EXAMPLE RUN")
    #     tpath = "%s/%s" % (self._dirpath, filepath)
    #     tpath = tpath.replace("//", "/")
    #     if not tpath.endswith(".py"):
    #         tpath += ".py"
    #     print("##: path: %s\n\n" % tpath)
    #     method = j.tools.jinja2.code_python_render(
    #         obj_key=obj_key, path=tpath, **kwargs)
    #     res = method()
    #     return res


    def _get_all(self,childclass_name=None):
        m = self._model_get(childclass_name)
        return m.get_all()

    def _reset(self,childclass_name=None):
        m = self._model_get(childclass_name)
        m.reset()

    def _count(self,childclass_name=None):
        counter = 0
        m = self._model_get(childclass_name)
        for obj_id in m.id_iterator:
            counter += 1
        return counter

    def _exists(self,childclass_name=None, **kwargs):
        res = self._find_obj(childclass_name=childclass_name,**kwargs)
        if len(res) > 1:
            raise RuntimeError("found too many items for :%s, args:\n%s\n%s" %(self.__class__.__name__, kwargs, res))
        elif len(res) == 1:
            return True
        else:
            return False

