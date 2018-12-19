from Jumpscale import j


JSBASE = j.application.JSBaseClass

from .ZOS import ZOS
from .ZOSVB import ZOSVB

class Builder(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.tools.builder"
        JSBASE.__init__(self)
        self._zos_client = None
        self._clients={}
        self._containers={}
        self._logger_enable()


    def zos_iso_download(self, zerotierinstance="",overwrite=True):

        if zerotierinstance:
            ztcl = j.clients.zerotier.get(zerotierinstance)
            zerotierid = ztcl.config.data['networkid']
            download = "https://bootstrap.grid.tf/iso/development/%s/development%20debug" % zerotierid
            dest = "/tmp/zos_%s.iso" % zerotierid
        else:
            download = "https://bootstrap.grid.tf/iso/development/0/development%20debug"
            dest = "/tmp/zos.iso"
        j.tools.prefab.local.core.file_download(download, to=dest, overwrite=overwrite)
        self._logger.info("iso downloaded ok.")
        return dest

    @property
    def vb_client(self):
        """
        virtualbox client
        """
        return j.clients.virtualbox.client

    def zos_get(self, zosclient_instance="builder", name=None):
        """
        zos client needs to be configured before it can be used at j.clients.zos.configure(...

        connect to existing zero-os
        :param name: when empty will be same name as the instance of zosclient
        :param zosclient_instance: is the instance name of zosclient get at j.clients.zos.get ...
        :return:
        """
        if name is None:
            name = zosclient_instance
        zosclient=j.clients.zos.get(zosclient_instance)
        return ZOS(zosclient=zosclient,name=name)


    def zos_vb_get(self, name="builder", zerotierinstance="", redis_port=4444, reset=False, memory=4000):
        """
        js_shell 'j.tools.builder.zos_vb_create(reset=False)'
        """
        vm = self.vb_client.vm_get(name)
        self._logger.debug(vm)

        if reset:
            vm.delete()

        if vm.exists:
            vm.start()
            self._logger.debug("vm %s started"%name)
        else:
            self._logger.info("will create zero-os:%s on redis port:%s" % (name, redis_port))
            #VM DOES NOT EXIST, Need to create the redis port should be free
            if j.sal.nettools.checkListenPort(redis_port):
                raise RuntimeError("cannot use port:%s is already in use" % redis_port)
            isopath = self.zos_iso_download(zerotierinstance)
            self._logger.info("zos vb create:%s (%s)" % (name, redis_port))
            vm.create(isopath=isopath, reset=reset, redis_port=redis_port,memory=memory)
            vm.start()

        from time import sleep

        if not j.sal.nettools.tcpPortConnectionTest("localhost", redis_port):
            retries = 60
            self._logger.info("wait till VM started (portforward on %s is on)." % redis_port)
            while retries:
                if j.sal.nettools.tcpPortConnectionTest("localhost", redis_port):
                    self._logger.info("VM port answers")
                    break
                else:
                    self._logger.debug("retry in 2s, redisport:%s"%redis_port)
                    sleep(2)
                retries -= 1
            else:
                raise RuntimeError("could not connect to VM port %s in 60 sec." % redis_port)

        r = j.clients.redis.get("localhost", redis_port, fromcache=False, ping=True, die=False, ssl=True)
        if r is None:
            retries = 100
            self._logger.info("wait till zero-os core redis on %s answers." % redis_port)
            while retries:
                r = j.clients.redis.get("localhost", redis_port, fromcache=False, ping=True, die=False, ssl=True)
                if r is not None:
                    self._logger.info("zero-os core redis answers")
                    break
                else:
                    self._logger.debug("retry in 2s")
                    sleep(2)
                retries -= 1
            else:
                raise RuntimeError("could not connect to VM port %s in 200 sec." % redis_port)

        self._redis = r

        zcl = j.clients.zos.get(name, data={"host": "localhost", "port": redis_port})
        retries = 200
        self._logger.info("internal files in ZOS are now downloaded for first time, this can take a while.")

        self._logger.info("check if we can reach zero-os client")
        while retries:
            if zcl.is_running():
                print("Successfully started ZOS on VirtualBox vm\n"
                      "with port forwarding {port} -> 6379 in VM\n"
                      "to get zos client run:\n"
                      "j.clients.zos.get('{instance}')\n"
                      "**DONE**".format(instance=name, port=redis_port))
                break
            else:
                self._logger.debug("couldn't connect to the created vm will retry in 2s")
                sleep(2)
            retries -= 1
        else:
            raise RuntimeError("could not connect to zeroos client in 400 sec.")

        self._logger.info("zero-os client active")
        self._logger.info("ping test start")
        pong = zcl.client.ping()
        self._logger.debug(pong)
        assert "PONG" in pong
        self._logger.info("ping test OK")

        if r.get("zos:active") != b'1':
            # self._logger.info("partition first time")
            # zcl.zerodbs.partition_and_mount_disks()
            # r.set("zos:active",1)
            pass

        self._logger.info("vm ready to be used")

        return ZOSVB(zosclient=zcl,name=name)


    def zos_vb_delete_all(self):
        """
        js_shell 'j.tools.builder.zos_vb_delete_all()'

        """
        self.vb_client.reset_all()



    def sync(self):
        """
        sync all code to the remote destinations, uses config as set in jumpscale.toml

        """



    def monitor(self):
        """
        look for changes in directories which are being pushed & if found push to remote nodes

        js_shell 'j.tools.develop.monitor()'

        """

        # self.sync()
        # nodes = self.nodes.getall()
        # paths = j.tools.develop.codedirs.getActiveCodeDirs()

        event_handler = MyFileSystemEventHandler()
        observer = Observer()
        for source in self.getActiveCodeDirs():
            self._logger.info("monitor:%s" % source)
            observer.schedule(event_handler, source.path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

    def test(self):
        """
        js_shell 'j.tools.builder.test()'
        """
        # self.zos_vb_delete_all()
        zos = self.zos_vb_get()
        container = zos.container_get("builder2") #default is the ub1804 flist
        container.start()
        res = container.container.system("ls /").get()
        assert "coreX\n" in res.stdout  #is a file on the root

        # container.build_python_jumpscale()
