from Jumpscale import j


class ZOSContainer(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    @url = jumpscale.clients.zoscmd.zoscontainer.1
    name = "" (S)
    ssh_addr = "127.0.0.1" (S)
    ssh_port = 22 (S)
    """

    def _init(self):
        self.ZOSNode = None  #links to the ZOSNode which hosts this ZOSContainer

    @property
    def zos_client(self):
        """
        return zos protocol client
        :return:
        """
        pass
        #implement caching at client side

    def ssh_client(self):
        """

        :return: ssh client to this container
        """
        pass
        #implement caching at client side

    def start(self):
        self.cache.delete("stop") #make sure that we will redo the stop action
        def do():
            pass
            #implement the logic how to start the container
        if not self.running(refresh=True,timeout=0):
            self.cache.get(key="start", method=do, refresh=True, die=True)
        assert self.running() == True

    def stop(self):
        """
        stop the container
        :return:
        """
        self.cache.delete("start") #make sure that we will redo the stop action
        self.cache.delete("running")
        def do():
            pass
        self.cache.get(key="stop", method=do, refresh=True, die=True)
        assert self.running() == False

    def running(self,timeout=60, refresh=True):
        """
        check container is running only using zos client
        :return:
        """
        def do():
            pass
        self.cache.get(key="running", method=do, timeout=timeout,refresh=refresh,expire=10, die=True)
        #expiration 0 means will always check again, sometimes makes sense to not recheck e.g. in 5 sec
        #refresh can be overruled so will check everytime (only relevant to use when expire is not 0)

        pass

    def reset(self):
        """
        remove all data (if there would be persistence in zos container)
        :return:
        """
        self.cache.reset() #all cached states need to go
        #TODO:

        pass

    def test(self):
        pass
        #do a basic test, look for client (e.g. start an ubuntu 18.04 container)
        #make connection
        #some test
    
    def __str__(self):
        return "zoscontainer:%-14s %-25s:%-4s" % (self.name, self.addr,self.port)

    __repr__ = __str__
