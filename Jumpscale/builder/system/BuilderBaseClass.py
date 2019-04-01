from Jumpscale import j

BaseClass = j.application.JSBaseClass

from Jumpscale.sal.bash.Profile import Profile

class builder_method(object):

    def __init__(self, **kwargs_):
        if "log" in kwargs_:
            self.log = j.data.types.bool.clean(kwargs_["log"])
        else:
            self.log = True
        if "done_check" in kwargs_:
            self.done_check = j.data.types.bool.clean(kwargs_["done_check"])
        else:
            self.done_check = True

    def __call__(self, func):

        def wrapper_action(*args, **kwargs):
            builder=args[0]
            args=args[1:]
            name= func.__name__

            done_key = name+"_"+j.data.hash.md5_string(str(args)+str(kwargs))

            if self.log:
                builder._log_debug("do once:%s"%name,data=kwargs)

            if "reset" in kwargs:
                reset = j.data.types.bool.clean(kwargs["reset"])
                kwargs.pop("reset")
            else:
                reset = False

            if reset:
                builder._done_reset()
                builder.reset()

            if name is not "_init":
                builder._init()
            if name == "install":
                builder.build()
            if name == "sandbox":
                builder.install()
                #only use "main" client, because should be generic usable
                zhub_client = kwargs.get("zhub_client", None)
                if not zhub_client and kwargs.get("flist_create"):
                    if not j.clients.zhub.exists(name="main"):
                        raise RuntimeError("cannot find main zhub client")
                    zhub_client = j.clients.zhub.get(name="main")
                    zhub_client.ping() #should do a test it works
                kwargs["zhub_client"] = zhub_client


            if name in ["start", "stop", "running"]:
                self.done_check = False

            if not self.done_check or not builder._done_check(done_key, reset):
                if self.log:
                    builder._log_debug("action:%s() start"%name)
                res = func(builder,*args,**kwargs)

                if name == "sandbox" and kwargs.get("flist_create", False):
                    res = builder._flist_create(zhub_client=zhub_client)

                if self.done_check:
                    builder._done_set(done_key)

                if self.log:
                    builder._log_debug("action:%s() done -> %s"%(name,res))

                return res
            else:
                builder._log_debug("action:%s() no need to do, was already done"%done_key)

        return wrapper_action


class BuilderBaseClass(BaseClass):
    """
    doc in /sandbox/code/github/threefoldtech/jumpscaleX/docs/Internals/Builders.md
    """
    def __init__(self):
        BaseClass.__init__(self)
        if hasattr(self.__class__,"NAME"):
            assert isinstance(self.__class__.NAME,str)
            self.DIR_BUILD = "/tmp/builders/{}".format(self.__class__.NAME)
            self.DIR_SANDBOX = "/tmp/package/{}".format(self.__class__.NAME)

        self._bash = None

    def state_sandbox_set(self):
        """
        bring builde in sandbox state
        :return:
        """
        self.state = self.state.SANDBOX
        self._bash = None
        
    def profile_home_select(self):
        if self.profile.state == "home":
            return
        self._profile_home_set()

    def profile_home_set(self):
        pass

    def _profile_home_set(self):

        self._bash = j.tools.bash.get(self._replace("{DIR_HOME}"))
        self.profile.state = "home"

        self.profile_home_set()

        self._profile_defaults_system()

        self.profile.env_set("PS1","HOME: ")

        self._log_info("home profile path in:%s"%self.profile.profile_path)


    def profile_builder_select(self):
        if self.profile.state == "builder":
            return
        self._profile_builder_set()

    def profile_builder_set(self):
        pass

    def _profile_defaults_system(self):

        self.profile.env_set("PYTHONHTTPSVERIFY",0)

        self.profile.env_set("LC_ALL","en_US.UTF-8")
        self.profile.env_set("LANG","en_US.UTF-8")

        self.profile.path_add("${PATH}",end=True)

    def _profile_builder_set(self):

        self._remove("{DIR_BUILD}/env.sh")
        self._bash = j.tools.bash.get(self._replace("{DIR_BUILD}"))

        self.profile.state = "builder"

        self.profile_builder_set()

        self.profile.env_set_part("LIBRARY_PATH","/usr/lib")
        self.profile.env_set_part("LIBRARY_PATH","/usr/local/lib")
        self.profile.env_set_part("LIBRARY_PATH","/lib")
        self.profile.env_set_part("LIBRARY_PATH","/lib/x86_64-linux-gnu")
        self.profile.env_set_part("LIBRARY_PATH","$LIBRARY_PATH",end=True)

        self.profile.env_set("LD_LIBRARY_PATH",self.profile.env_get("LIBRARY_PATH")) #makes copy
        self.profile.env_set("LDFLAGS","-L'%s'"%self.profile.env_get("LIBRARY_PATH"))

        self.profile.env_set_part("CPPPATH","/usr/include")
        self.profile.env_set("CPATH",self.profile.env_get("CPPPATH"))
        self.profile.env_set("CPPFLAGS","-I'%s'"%self.profile.env_get("CPPPATH"))

        self.profile.env_set("PS1","PYTHONBUILDENV: ")

        self._profile_defaults_system()

        self.profile.path_add(self._replace("{DIR_BUILD}/bin"))

        self._log_info("build profile path in:%s"%self.profile.profile_path)

    def profile_sandbox_select(self):
        if self.profile.state == "sandbox":
            return
        self._profile_sandbox_set()


    def profile_sandbox_set(self):
        pass

    def _profile_sandbox_set(self):

        self._bash = j.tools.bash.get("/sandbox/env.sh")

        self.profile.state = "sandbox"

        self.profile.path_add("/sandbox/bin")

        self.profile.env_set("PYTHONHTTPSVERIFY",0)

        self.profile.env_set_part("PYTHONPATH","/sandbox/lib")
        self.profile.env_set_part("PYTHONPATH","/sandbox/lib/jumpscale")

        self.profile.env_set("LC_ALL","en_US.UTF-8")
        self.profile.env_set("LANG","en_US.UTF-8")
        self.profile.env_set("PS1","JSX: ")


        self.profile_sandbox_set()

        self.profile.path_delete("${PATH}")

        if j.core.platformtype.myplatform.isMac:
            self.profile.path_add("${PATH}",end=True)

        self.profile.env_set_part("PYTHONPATH","$PYTHONPATH",end=True)

        self._log_info("sandbox profile path in:%s"%self.profile.profile_path)


    @property
    def bash(self):
        if not self._bash:
            self._bash = j.tools.bash.sandbox
        return self._bash

    @property
    def profile(self):
        return self.bash.profile

    def _replace(self, txt,args={}):
        """

        :param txt:
        :return:
        """
        for key,item in self.__dict__.items():
            if key.upper() == key:
                args[key] = item
        res =  j.core.tools.text_replace(content=txt, args=args, text_strip=True)
        if res.find("{")!=-1:
            raise RuntimeError("replace was not complete, still { inside, '%s'"%res)
        return res

    def _execute(self, cmd, die=True, args={}, timeout=600,
                 replace=True, showout=True, interactive=False):
        """

        :param cmd:
        :param die:
        :param showout:
        :param profile:
        :param replace:
        :param interactive:
        :return: (rc, out, err)
        """
        self._log_debug(cmd)
        if replace:
            cmd = self._replace(cmd,args=args)
        if cmd.strip() == "":
            raise RuntimeError("cmd cannot be empty")

        cmd="cd %s\n. %s\n%s"%(self.bash.path,self.profile.profile_path,cmd)
        name = self.__class__._name
        name = name.replace("builder","")
        path = "%s/builder_%s.sh"%(self.bash.path,name)
        self._log_debug("execute: '%s'"%path)

        if die:
            if cmd.find("set -xe")==-1 and cmd.find("set -e")==-1:
                cmd="set -ex\n%s"%(cmd)

        j.sal.fs.writeFile(path,contents=cmd)

        return j.sal.process.execute("bash %s"%path, cwd=None, timeout=timeout, die=die,
                                             args=args, interactive=interactive, replace=False, showout=showout)

    def _copy(self, src, dst, deletefirst=False,ignoredir=None,ignorefiles=None,deleteafter=False):
        """
        
        :param src: 
        :param dst: 
        :param deletefirst: 
        :param ignoredir: the following are always in, no need to specify ['.egg-info', '.dist-info', '__pycache__']
        :param ignorefiles: the following are always in, no need to specify: ["*.egg-info","*.pyc","*.bak"]
        :param deleteafter, means that files which exist at destination but not at source will be deleted
        :return: 
        """
        src = self._replace(src)
        dst = self._replace(dst)
        if j.builder.tools.file_is_dir:
            j.builder.tools.copyTree(src, dst, keepsymlinks=False, deletefirst=deletefirst, overwriteFiles=True,
                                 ignoredir=ignoredir, ignorefiles=ignorefiles, recursive=True, rsyncdelete=deleteafter,
                                 createdir=True)
        else:
            j.builder.tools.file_copy(src, dst, recursive=False, overwrite=True)

    def _write(self, path, txt):
        """
        will use the replace function on text and on path
        :param path:
        :param txt:
        :return:
        """
        path = self._replace(path)
        txt = self._replace(txt)
        j.sal.fs.writeFile(path,txt)

    def _remove(self, path):
        """
        will use the replace function on text and on path
        :param path:
        :return:
        """
        self._log_debug("remove:%s"%path)
        path = self._replace(path)

        j.sal.fs.remove(path)

    @property
    def system(self):
        return j.builder.system

    @property
    def tools(self):
        """
        Builder tools is a set of tools to perform the common tasks in your builder (e.g read a file
        , write to a file, execute bash commands and many other handy methods that you will probably need in your builder)
        :return:
        """
        return j.builder.tools

    def reset(self):
        """
        reset the state of your builder, important to let the state checking restart
        :return:
        """
        self._done_reset()

    @builder_method()
    def build(self):
        """
        :return:
        """
        return

    @builder_method()
    def install(self):
        """
        will build as first step
        :return:
        """
        return

    @builder_method()
    def sandbox(self, zhub_client):
        '''
        when zhub_client None will look for j.clients.get("test"), if not exist will die
        '''
        return

    @property
    def startup_cmds(self):
        return []

    def start(self):
        for startupcmd in self.startup_cmds:
            startupcmd.start()

    def stop(self):
        for startupcmd in self.startup_cmds:
            startupcmd.stop()

    def running(self):
        for startupcmd in self.startup_cmds:
            if startupcmd.running() == False:
                return False
        return True

    @builder_method()
    def _flist_create(self, zhub_client=None):
        """
        build a flist for the builder and upload the created flist to the hub

        This method builds and optionally upload the flist to the hub

        :param hub_instance: zerohub client to use to upload the flist, defaults to None if None
        the flist will be created but not uploaded to the hub
        :param hub_instance: j.clients.zhub instance, optional
        :return: the flist url
        """

        # self.copy_dirs(self.root_dirs, self.DIR_SANDBOX)
        # self.write_files(self.root_files, self.DIR_SANDBOX)

        # if self.startup:
        #     #TODO differently, use info from self.startup_cmds
        #     file_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, '.startup.toml')
        #     j.builder.tools.file_ensure(file_dest)
        #     j.builder.tools.file_write(file_dest, self.startup)

        j.shell()

        j.tools.sandboxer.copyTo(src, dst)


        if j.core.platformtype.myplatform.isLinux:
            ld_dest = j.sal.fs.joinPaths(self.DIR_SANDBOX, 'lib64/')
            j.builder.tools.dir_ensure(ld_dest)
            j.sal.fs.copyFile('/lib64/ld-linux-x86-64.so.2', ld_dest)

        # if zhub_client:
        #for now only upload to HUB
        self._log_info("uploading flist to the hub")
        return zhub_client.sandbox_upload(self.NAME, self.DIR_SANDBOX)
        # else:
        #     tarfile = '/tmp/{}.tar.gz'.format(self.NAME)
        #     j.sal.process.execute('tar czf {} -C {} .'.format(tarfile, self.DIR_SANDBOX))
        #     return tarfile



    def clean(self):
        """
        removes all files as result from building
        :return:
        """
        self.uninstall()
        return

    def uninstall(self):
        """
        optional, removes installed, build & sandboxed files
        :return:
        """
        return

    def test(self):
        """
        -  a basic test to see if the build was successfull
        - will automatically call start() at start
        - is optional
        """
        raise RuntimeError("not implemented")

    def test_api(self,ipaddr="localhost"):
        """
        - will test the api on specified ipaddr e.g. rest calls, tcp calls, port checks, ...
        """
        raise RuntimeError("not implemented")

    def test_zos(self,zhub_client,zos_client):
        """

        - a basic test to see if the build was successfull
        - will automatically call sandbox(zhub_client=zhub_client) at start
        - will start the container on specified zos_client with just build flist
        - will call .test_api() with ip addr of the container

        """
        raise RuntimeError("not implemented")
