from Jumpscale import j

BaseClass = j.application.JSBaseClass

from Jumpscale.clients.zero_hub_direct.HubDirectClient import HubDirectClient

class builder_method(object):

    def __init__(self, **kwargs_):
        if "log" in kwargs_:
            self.log = j.data.types.bool.clean(kwargs_["log"])
        else:
            self.log = True

    def __call__(self, func):
        print("Inside __call__()")
        log = self.log

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
            if not self._done_check(name, reset):
                if log:
                    self._log_debug("action:%s() start"%name)
                res = func(self,*args,**kwargs)

                if name == "sandbox":
                    res = self._flist_create(zhub_client=zhub_client)

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

    @builder_method()
    def install(self):
        """
        will build as first step
        :return:
        """
        return

    @builder_method()
    def sandbox(self, zhub_client=None):
        '''
        when zhub_client None will look for j.clients.get("test"), if not exist will die
        '''
        return


    def _flist_create(self, zhub_client=None):
        """
        build a flist for the builder and upload the created flist to the hub

        This method builds and optionally upload the flist to the hub

        :param hub_instance: instance name of the zerohub client to use to upload the flist, defaults to None if None
        the flist will be created but not uploaded to the hub
        :param hub_instance: str, optional
        :raises j.exceptions.Input: raised if the zerohub client instance does not exist in the config manager
        :return: path to the tar.gz created
        :rtype: str
        """


        if self.startup:
            file_dest = j.sal.fs.joinPaths(self._sandbox_dir, '.startup.toml')
            j.builder.tools.file_ensure(file_dest)
            j.builder.tools.file_write(file_dest, self.startup)

        if j.core.platformtype.myplatform.isLinux:
            ld_dest = j.sal.fs.joinPaths(self._sandbox_dir, 'lib64/')
            j.builder.tools.dir_ensure(ld_dest)
            j.sal.fs.copyFile('/lib64/ld-linux-x86-64.so.2', ld_dest)


        huburl= zhub_client.upload(self._sandbox_dir)  #does the tar

        # self._log_info('building flist')
        # tarfile = '/tmp/{}.tar.gz'.format(self.NAME)
        # j.sal.process.execute('tar czf {} -C {} .'.format(tarfile, sandbox_dir))

        # if not j.clients.zhub.exists(name=hub_instance):
        #     raise j.exceptions.Input("hub instance %s does not exists, can't upload to the hub" % hub_instance)
        # hub = j.clients.zhub.get(hub_instance)
        # hub.authenticate()
        # self._log_info("uploading flist to the hub")
        # hub.upload(tarfile)
        # self._log_info("uploaded at https://hub.grid.tf/{}/{}.flist".format(hub.username,self.NAME))

        return tarfile
