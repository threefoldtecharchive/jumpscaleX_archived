from Jumpscale import j

from .JSBase import JSBase


class JSFactoryBase(JSBase):

    _location = None
    _CHILDCLASS = None
    _children = {}

    def get(self, id=None, name="default", child_class=None, **kwargs):
        if name not in JSFactoryBase._children:
            if child_class is None:
                if self.__class__._CHILDCLASS is None:
                    raise RuntimeError("__class__._CHILDCLASS should be set")
                child_class = self.__class__._CHILDCLASS
            o = child_class(id=id, name=name,data=kwargs)
            JSFactoryBase._children[name] = o
        return JSFactoryBase._children[name]

    def count(self, child_class=None):
        return self._count(child_class=child_class)

    def find(self, child_class=None, **kwargs):
        """

        :param child_class: optional, if not given then will use __class__._CHILDCLASS
        :param kwargs: e.g. color="red",...
        :return: list of the objects
        """
        if child_class is None:
            if self.__class__._CHILDCLASS is None:
                raise RuntimeError("__class__._CHILDCLASS should be set")
            child_class = self.__class__._CHILDCLASS

        if len(kwargs) == 1:
            kwargs["name"] = kwargs[0]  # if only one then will be the name
        m = self._get_model(child_class)
        propnames = [i for i in kwargs.keys()]
        propnames_keys_in_schema = [
            item.name for item in m.schema.index_key_properties if item.name in propnames]

        res = []
        if len(propnames_keys_in_schema) > 0:
            # we can try to find this config
            res = m.get_from_keys(**kwargs)

        res2 = []
        for item in res:
            res2.append(child_class(id=item.id))

        return res2

    def _load(self, klass):
        name = klass.__name__
        self.__dict__[name] = klass
        self.__dict__[name].coordinator = self

    def _example_run(self, filepath="example", obj_key="main", **kwargs):
        """
        the example file will be copied to {DIR_VAR}/CODEGEN/$uniquekey and executed there
        template engine jinja is used to apply kwargs onto this file

        :param filepath: name of file to execute can be e.g. example.py or example or examples/example1.py
                        is always relative to the file you call this function from
        :param kwargs: the arguments which will be given to the template engine
        :param obj_key: is the name of the function we will look for to execute, cannot have arguments
               to pass arguments to the example script, use the templating feature

        :return: result = is the result of the method called

        """
        print("##: EXAMPLE RUN")
        tpath = "%s/%s" % (self._dirpath, filepath)
        tpath = tpath.replace("//", "/")
        if not tpath.endswith(".py"):
            tpath += ".py"
        print("##: path: %s\n\n" % tpath)
        method = j.tools.jinja2.code_python_render(
            obj_key=obj_key, path=tpath, **kwargs)
        res = method()
        return res

    def _get_model(self, child_class=None):
        if child_class is None:
            if self.__class__._CHILDCLASS is None:
                raise RuntimeError("__class__._CHILDCLASS should be set")
            child_class = self.__class__._CHILDCLASS
        if child_class._SCHEMATEXT is not None:
            if "_MODEL" not in child_class.__dict__ or child_class._MODEL is None:
                child_class._MODEL = j.application.bcdb_system.model_get_from_schema(
                    child_class._SCHEMATEXT)
        m = child_class._MODEL
        return m

    def _get_all(self, child_class=None):
        m = self._get_model(child_class)
        return m.get_all()

    def _reset(self, child_class=None):
        m = self._get_model(child_class)
        m.reset()

    def _count(self, child_class=None):
        counter = 0
        m = self._get_model(child_class)
        for obj_id in m.id_iterator:
            counter += 1
        return counter

    def _exists(self, *args, child_class=None, **kwargs):
        if len(args) == 1:
            kwargs["name"] = args[0]  # if only one then will be the name
        m = self._get_model(child_class)
        propnames = [i for i in kwargs.keys()]
        propnames_keys_in_schema = [
            item.name for item in m.schema.index_key_properties if item.name in propnames]
        if len(propnames_keys_in_schema) > 0:
            # we can try to find this config
            res = m.get_from_keys(**kwargs)
            if len(res) > 1:
                raise RuntimeError("found too many items for :%s, args:\n%s\n%s" %
                                   (self.__class__.__name__, kwargs, res))
            elif len(res) == 1:
                return True
            else:
                return False
        else:
            j.shell()
            raise RuntimeError("args:%s do not exist in data obj (is it indexed, has it * appended)" % args)
