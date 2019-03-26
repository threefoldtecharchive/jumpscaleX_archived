from Jumpscale import j

BaseClass = j.application.JSBaseClass

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
            if self.log:
                builder._log_debug("do once:%s"%name)
            if name is not "_init":
                builder._init()
            if name == "install":
                builder.build()
            if name == "sandbox":
                builder.install()
                zhub_client = args["zhub_client"]
                if not zhub_client:
                    if not j.clients.zhub.exists(name="test"):
                        raise RuntimeError("cannot find test zhub client")
                    zhub_client = j.clients.zhub.get(name="test")
                else:
                    if not hasattr(zhub_client, "sandbox_upload"):
                        raise RuntimeError("specify valid zhub_client")
                zhub_client.ping() #should do a test it works
                kwargs["zhub_client"] = zhub_client

            if "reset" in kwargs:
                reset = kwargs["reset"]
            else:
                reset = False

            if name in ["start", "stop", "running"]:
                self.done_check = False

            if not self.done_check or not builder._done_check(name, reset):
                if self.log:
                    builder._log_debug("action:%s() start"%name)
                res = func(self,*args,**kwargs)

                if name == "sandbox":
                    if "flist_create" in kwargs and kwargs["flist_create"]:
                        res = builder._flist_create(zhub_client=kwargs["zhub_client"])
                if self.done_check:
                    builder._done_set(name)
                if self.log:
                    builder._log_debug("action:%s() done -> %s"%(name,res))
                return res
            else:
                builder._log_debug("action:%s() no need to do, was already done"%name)

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

    @builder_method(log=False, done_check=True)
    def install(self):
        """
        will build as first step
        :return:
        """
        return

    @builder_method(log=False, done_check=True)
    def sandbox(self, zhub_client=None):
        '''
        when zhub_client None will look for j.clients.get("test"), if not exist will die
        '''
        return

    @property
    def startup_cmds(self):
        raise RuntimeError("not implemented")

    @builder_method(log=False, done_check=True)
    def start(self):
        for startupcmd in self.startup_cmds:
            startupcmd.start()

    @builder_method(log=False, done_check=True)
    def stop(self):
        for startupcmd in self.startup_cmds:
            startupcmd.stop()

    @builder_method(log=False, done_check=True)
    def running(self):
        for startupcmd in self.startup_cmds:
            if startupcmd.running() == False:
                return False
        return True

    @builder_method(log=False, done_check=True)
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
