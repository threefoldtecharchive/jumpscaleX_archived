from Jumpscale import j

from .JSBase import JSBase


class KosmosServices():

    def __init__(self,factory):
        self._factory = factory

    def _empty_js_obj(self):
        for key,val in self.__dict__.items():
            if not key.startswith("_"):
                self.__dict__[key]._empty_js_obj()
                del self.__dict__[key]
                self.__dict__[key]=None

    def __getattr__(self, name):
        #if private then just return
        if name.startswith("_"):
            return self.__dict__[name]
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
        return [item.name for item in m._get_all()]

    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name]=value
            return
        raise RuntimeError("readonly")

    def __str__(self):
        try:
            out = "%s\n%s\n"%(self.__class__.__name__,self.data)
        except:
            out = str(self.__class__)+"\n"
            out+=j.core.text.prefix(" - ", self.data)
        return out

    __repr__ = __str__


class JSFactoryBase(JSBase):

    _location = None
    _CHILDCLASS = None
    _children = {}

    def __init__(self):
        JSBase.__init__(self)
        if "clients" in self.__location__:
            self.instances = KosmosServices(self)
        else:
            self.services = KosmosServices(self)
        self.__model = None
        self._init()


    def _empty_js_obj(self):
        self.__dict__["_children"] = {}
        if "clients" in self.__location__:
            self.instances._empty_js_obj()
        else:
            self.services._empty_js_obj()

    @property
    def name(self):
        return self.__location__.split(".")[-1]

    def new(self,name,**kwargs):
        """
        :param name: for the service
        :param kwargs: the data elements
        :return: the service
        """
        data = self._model.new()
        data.name = name
        if kwargs is not {}:
            data.data_update(data=kwargs)

        child_class = self._childclass_selector(dataobj=data,kwargs=kwargs)

        o = child_class(factory=self,dataobj=data)

        o._data_trigger_new()
        self._isnew = True

        self.__class__._children[data.name] = o
        return self.__class__._children[data.name]


    def _childclass_selector(self,dataobj,kwargs):
        """
        gives a creator of a factory the ability to change the type of child to be returned
        :return:
        """
        if self.__class__._CHILDCLASS is None:
            raise RuntimeError("__class__._CHILDCLASS should be set")
        return self.__class__._CHILDCLASS

    def get(self,name=None,id=None,die=True ,create_new=True,**kwargs):
        """
        :param id: id of the obj to find, is a unique id
        :param name: of the object, can be empty when searching based on id or the search criteria (kwargs)
        :param search criteria (if name not used) or data elements for the new one being created
        :param die, means will give error when object not found
        :param create_new, if True it will automatically create a new one
        :return: the service
        """
        if name is not None and name  in self.__class__._children:
            return self.__class__._children[name]

        if id is not None:
            data = self._model.get(id=id)
            name = data.name
        else:
            if name is None:
                #need to find based on kwargs
                res = self._find_obj(**kwargs)
                if len(res)<1:
                    return self._error_input_raise("Dit not find services for :%s, search criteria:\n%s"%(self.__location__,kwargs))
                elif len(res)>1:
                    return self._error_input_raise("Found more than 1 service for :%s, search criteria:\n%s"%(self.__location__,kwargs))
                data = res[0]
                name = data.name
            else:
                res = self._find_obj(name=name)
                if len(res)<1:
                    if create_new:
                        return self.new(name=name,**kwargs)
                    if die:
                        return self._error_input_raise("Did not find the service for '%s', name looking for:\n%s"%(self.__location__,name))
                    else:
                        return None
                elif len(res)>1:
                    return self._error_input_raise("Found more than 1 service for '%s', name looking for:\n%s"%(self.__location__,name))
                else:
                    data=res[0]

        if self.__class__._CHILDCLASS is None:
            raise RuntimeError("__class__._CHILDCLASS should be set")
        child_class = self.__class__._CHILDCLASS
        o = child_class(factory=self,dataobj=data)
        self.__class__._children[name] = o
        return self.__class__._children[name]

    def reset(self):
        """
        will remove all the instances, be carefull
        :return:

        """
        for item in self.find():
            item.delete()

    def count(self):
        return self._count()

    @property
    def _model(self):
        if self.__model is None:
            if self.__class__._CHILDCLASS is None:
                raise RuntimeError("__class__._CHILDCLASS should be set")
            child_class = self.__class__._CHILDCLASS
            self.__model = j.application.bcdb_system.model_get_from_schema(child_class._SCHEMATEXT)
        return self.__model


    def _find_obj(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the objects
        """
        if len(kwargs)>0:
            propnames = [i for i in kwargs.keys()]
            propnames_keys_in_schema = [item.name for item in self._model.schema.properties_index_keys if item.name in propnames]
            if len(propnames_keys_in_schema) > 0:
                # we can try to find this config
                return self._model.get_from_keys(**kwargs)
            else:
                raise RuntimeError("cannot find obj with kwargs:\n%s\n in %s\nbecause kwargs do not match, is there * in schema"%(kwargs,self))
            return []
        else:
            return self._model.get_all()


    def find(self, **kwargs):
        """
        :param kwargs: e.g. color="red",...
        :return: list of the objects
        """
        res=[]
        for dataobj in self._find_obj( **kwargs):
            res.append(self.get(dataobj.id))
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


    def _get_all(self):
        m = self._model
        return m.get_all()

    def _reset(self):
        m = self._model
        m.reset()

    def _count(self):
        counter = 0
        m = self._model
        for obj_id in m.id_iterator:
            counter += 1
        return counter

    def _exists(self, **kwargs):
        res = self._find_obj(**kwargs)
        if len(res) > 1:
            raise RuntimeError("found too many items for :%s, args:\n%s\n%s" %(self.__class__.__name__, kwargs, res))
        elif len(res) == 1:
            return True
        else:
            return False

