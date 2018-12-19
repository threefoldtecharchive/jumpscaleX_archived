from Jumpscale import j

from .JSBase import JSBase


class JSFactoryBase(JSBase):

    _location = None
    _test_runs = {}
    _test_runs_error = {}


    def _load(self,klass):
        name = klass.__name__
        self.__dict__[name] = klass
        self.__dict__[name].coordinator = self

    def _example_run(self,filepath="example",obj_key="main",**kwargs):
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
        print ("##: EXAMPLE RUN")
        tpath = "%s/%s"%(self._dirpath,filepath)
        tpath = tpath.replace("//","/")
        if not tpath.endswith(".py"):
            tpath+=".py"
        print ("##: path: %s\n\n" % tpath)
        method = j.tools.jinja2.code_python_render(obj_key=obj_key, path=tpath,**kwargs)
        res = method()
        return res

    def _get_model(self,child_class=None):
        if child_class is None:
            child_class = self._CHILDCLASS
        if child_class._SCHEMATEXT is not None:
            if "_MODEL" not in child_class.__dict__ or child_class._MODEL is None:
                child_class._MODEL = j.application.bcdb_system.model_get_from_schema(child_class._SCHEMATEXT)
        m=child_class._MODEL
        return m

    def _get_all(self,child_class=None):
        m = self._get_model(child_class)
        return m.get_all()

    def _reset(self,child_class=None):
        m = self._get_model(child_class)
        m.reset()

    def _count(self,child_class=None):
        counter=0
        m = self._get_model(child_class)
        for obj_id in m.id_iterator:
            counter+=1
        return counter

    def _exists(self,*args,child_class=None,**kwargs):
        if len(args)==1:
            kwargs["name"]=args[0] #if only one then will be the name
        m = self._get_model(child_class)
        propnames = [i for i in kwargs.keys()]
        propnames_keys_in_schema = [item.name for item in m.schema.index_key_properties if item.name in propnames]
        if len(propnames_keys_in_schema)>0:
            #we can try to find this config
            res = m.get_from_keys(**kwargs)
            if len(res)>1:
                raise RuntimeError("found too many items for :%s, args:\n%s\n%s"%(self.__class__.__name__,kwargs,res))
            elif len(res)==1:
                return True
            else:
                return False
        else:
            j.shell()
            raise RuntimeError("args:%s do not exist in data obj (is it indexed, has it * appended)"%args)


    def _test_error(self,name,error):
        j.errorhandler.try_except_error_process(e,die=False)
        self.__class__._test_runs_error[name] = error

    def _test_run(self,name="",obj_key="main",**kwargs):
        """

        :param name: name of file to execute can be e.g. 10_test_my.py or 10_test_my or subtests/test1.py
                    the tests are found in subdir tests of this file

                if empty then will use all files sorted in tests subdir, but will not go in subdirs

        :param obj_key: is the name of the function we will look for to execute, cannot have arguments
               to pass arguments to the example script, use the templating feature, std = main


        :return: result of the tests

        """

        res = self.__test_run(name=name,obj_key=obj_key,**kwargs)
        if self.__class__._test_runs_error != {}:
            for key,e in self.__class__._test_runs_error.items():
                self._logger.error("ERROR FOR TEST: %s\n%s"%(key,e))
            self._logger.error("SOME TESTS DIT NOT COMPLETE SUCCESFULLY")
        else:
            self._logger.info("ALL TESTS OK")
        return res

    def __test_run(self,name="",obj_key="main",**kwargs):

        self._logger_enable()
        self._logger.info("##: TEST RUN")
        if name.endswith(".py"):
            name = name[:-3]
        if name != "":
            tpath = "%s/tests/%s"%(self._dirpath,name)
            tpath = tpath.replace("//","/")
            tpath+=".py"
            if not j.sal.fs.exists(tpath):
                for item in j.sal.fs.listFilesInDir("%s/tests"%self._dirpath, recursive=False, filter="*.py"):
                    bname = j.sal.fs.getBaseName(item)
                    if "_" in bname:
                        bname2 = "_".join(bname.split("_",1)[1:])  #remove part before first '_'
                    else:
                        bname2=bname
                    if bname2.startswith(name):
                        self.__test_run(name=bname,obj_key=obj_key,**kwargs)
                        return
                return self._test_error(name,RuntimeError("Could not find, test:%s in %s/tests/"%(name,self._dirpath)))

            self._logger.debug("##: path: %s\n\n" % tpath)
        else:
            items = [j.sal.fs.getBaseName(item) for item in
                j.sal.fs.listFilesInDir("%s/tests"%self._dirpath, recursive=False, filter="*.py")]
            items.sort()
            for name in items:
                self.__test_run(name=name,obj_key=obj_key,**kwargs)


            return

        method = j.tools.loader.load(obj_key=obj_key, path=tpath,reload=False,md5="")
        try:
            res = method(self=self,**kwargs)
        except Exception as e:
            j.errorhandler.try_except_error_process(e,die=False)
            self.__class__._test_runs_error[name]=e
            return e
        self.__class__._test_runs[name]=res
        return res
