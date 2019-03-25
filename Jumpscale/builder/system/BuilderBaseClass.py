from Jumpscale import j

BaseClass = j.application.JSBaseClass

class action:

    def __init__(self, **kwargs):
        self.depends = kwargs.get('depends', [])
        self.log = kwargs.get('log', True)

    def __call__(self, func):
        def wrapper_action(*args, **kwargs):
            builder = args[0]  # self of the builder
            reset = kwargs.get("reset", False)
            for dep in self.depends:
                if hasattr(builder, dep):
                    if builder._done_check(dep) and not reset:
                        builder._log_debug("{} already done".format(dep))
                    else:
                        act = getattr(builder, dep)
                        act(reset=reset)
                else:
                    raise RuntimeError("Builder {} doesn't have {} action, please check your dependencies"
                                       .format(builder.NAME, dep))

            if builder._done_check(func.__name__) and not reset:
                builder._log_debug("{} already done".format(func.__name__))
            else:
                func(*args, **kwargs)
                builder._done_set(func.__name__)

        return wrapper_action

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
        print("Inside __call__()")
        log = self.log
        done_check = self.done_check

        def wrapper_action(*args, **kwargs):
            self=args[0]
            args=args[1:]
            name= func.__name__
            if log:
                self._log_debug("do once:%s"%name)
            if name is not "_init":
                self._init()
            if name == "install":
                self.build()
            if name == "sandbox":
                self.install()
                zhub_client = args["zhub_client"]
                if not zhub_client:
                    # from Jumpscale.clients.zero_hub.ZeroHubClient import ZeroHubClient
                    if not j.clients.zhubdirect.exists(name="test"): #TODO:*1 is this the right client?
                        raise RuntimeError("cannot find zhub client")
                    zhub_client = j.clients.zhubdirect.get(name="test")
                else:
                    if not isinstance(zhub_client,HubDirectClient):
                        raise RuntimeError("specify valid zhub_client")
                zhub_client.ping() #should do a test it works
                args["zhub_client"] = zhub_client

            if "reset" in kwargs:
                reset = kwargs["reset"]
            else:
                reset = False

            if name in ["start","stop","running"]:
                done_check = False

            if not done_check or not self._done_check(name, reset):
                if log:
                    self._log_debug("action:%s() start"%name)
                res = func(self,*args,**kwargs)

                if name == "sandbox":
                    res = self._flist_create(zhub_client=zhub_client)
                if done_check:
                    self._done_set(name)
                if log:
                    self._log_debug("action:%s() done -> %s"%(name,res))
                return res
            else:
                self._log_debug("action:%s() no need to do, was already done"%name)

        return wrapper_action


class BuilderBaseClass(BaseClass):
    def __init__(self):
        BaseClass.__init__(self)
        if hasattr(self.__class__,"NAME"):
            assert isinstance(self.__class__.NAME,str)
            self._sandbox_dir = "/tmp/builders/{}".format(self.__class__.NAME)

    @property
    def system(self):
        return j.builder.system

    @property
    def tools(self):
        return j.builder.tools

    def reset(self):
        self._done_reset()

    @action(depends=["_init"])
    def install(self):
        """
        will build as first step
        :return:
        """
        return

    @action(depends=["build"])
    def sandbox(self, zhub_client=None):
        '''
        when zhub_client None will look for j.clients.get("test"), if not exist will die
        '''
        return

    @property
    def startup_cmds(self):
        raise RuntimeError("not implemented")

    @action(depends=["build"])
    def start(self):
        for startupcmd in self.startup_cmds:
            startupcmd.start()

    @action(depends=["start"])
    def stop(self):
        for startupcmd in self.startup_cmds:
            startupcmd.stop()

    @action(depends=[])
    def running(self):
        for startupcmd in self.startup_cmds:
            if startupcmd.running() == False:
                return False
        return True

    @action(depends=["sandbox"])
    def _flist_create(self, zhub_client=None):
        """
        build a flist for the builder and upload the created flist to the hub

        This method builds and optionally upload the flist to the hub

        :param hub_instance: zerohub client to use to upload the flist, defaults to None if None
        the flist will be created but not uploaded to the hub
        :param hub_instance: j.clients.zhub instance, optional
        :return: path to the tar.gz created or the url of the uploaded flist
        :rtype: str
        """

        self.copy_dirs(self.root_dirs, self._sandbox_dir)
        self.write_files(self.root_files, self._sandbox_dir)

        if self.startup:
            file_dest = j.sal.fs.joinPaths(self._sandbox_dir, '.startup.toml')
            j.builder.tools.file_ensure(file_dest)
            j.builder.tools.file_write(file_dest, self.startup)

        if j.core.platformtype.myplatform.isLinux:
            ld_dest = j.sal.fs.joinPaths(self._sandbox_dir, 'lib64/')
            j.builder.tools.dir_ensure(ld_dest)
            j.sal.fs.copyFile('/lib64/ld-linux-x86-64.so.2', ld_dest)

        if zhub_client:
            self._log_info("uploading flist to the hub")
            return zhub_client.sandbox_upload(self.NAME, self.sandbox_dir)
        else:
            tarfile = '/tmp/{}.tar.gz'.format(self.NAME)
            j.sal.process.execute('tar czf {} -C {} .'.format(tarfile, self._sandbox_dir))
            return tarfile
