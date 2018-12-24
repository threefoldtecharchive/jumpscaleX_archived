from Jumpscale import j

JSBASE = j.application.JSBaseClass


class WIC_Factory(j.builder._BaseClass):

    def __init__(self):
        self.__jslocation__ = "j.tools.wic"
        self.defPassword = "rooter"
        JSBASE.__init__(self)

    def get(self, ipaddr, passwd=""):
        return WIC()

    def install(self, wics=""):
        """
        e.g.

        wics e.g. wics="192.168.16.106,192.168.16.117,192.168.16.159,192.168.16.116,192.168.16.181,192.168.16.161,192.168.16.158"
        """
        if wics == "":
            wics = "192.168.16.106,192.168.16.159,192.168.16.116,192.168.16.161"  # 192.168.16.117,192.168.16.181,192.168.16.158  "

        wicips = [item.strip() for item in wics.split(",")]

        def update(ipaddr):

            import time

            e = j.tools.executor.getSSHBased(ipaddr, port=22, login="root", passwd="rooter", usecache=False)

            self._logger.debug("##### START UPDATE PROCESS, THIS CAN TAKE 3 MIN")
            cmd = "cd /tmp;wget http://downloads.openwrt.org/chaos_calmer/15.05.1/ar71xx/generic/openwrt-15.05.1-ar71xx-generic-gl-inet-6416A-v1-squashfs-factory.bin;sysupgrade openwrt-15.05.1-ar71xx-generic-gl-inet-6416A-v1-squashfs-factory.bin"
            res = e.sshclient.client.exec_command(cmd)

            # wait till reboot
            state = "update"
            t = j.data.time.getTimeEpoch()
            timeout = t + 300
            while t < timeout and state == "update":
                res = j.sal.nettools.pingMachine(ipaddr, pingtimeout=1)
                if res is False:
                    state = "reboot"
                time.sleep(1)

            if state != "reboot":
                raise RuntimeError("cannot update %s, did not happen in 300 sec." % ipaddr)

            e.sshclient.close()

            self._logger.debug("##### WIC IS NOW REBOOTING")

            t = j.data.time.getTimeEpoch()
            timeout = t + 180
            while t < timeout and state == "reboot":
                res = j.sal.nettools.pingMachine(ipaddr, pingtimeout=2)
                if res:
                    state = "up"
                time.sleep(2)

            if state != "up":
                raise RuntimeError("cannot update %s, reboot did not happen in 180 sec." % ipaddr)

            self._logger.debug("##### WIC IS LIFE, UPDATE PACKAGES")

            time.sleep(5)

            e = j.tools.executor.getSSHBased(ipaddr, port=22, login="root", passwd="rooter", usecache=False)
            # e.sshclient.execute("opkg install luci")
            e.sshclient.execute("opkg update")

        def sw(ipaddr):

            e = j.tools.executor.getSSHBased(ipaddr, port=22, login="root", passwd="rooter", usecache=False)
            self._logger.debug("%s:UPDATE OPKG" % ipaddr)
            e.sshclient.execute("opkg update")
            e.sshclient.execute("opkg install bash")
            e.sshclient.execute("opkg install fastd")


        # wics=[]
        for wicip in wicips:
            # j.actions.add(update, kwargs={"ipaddr":wicip}, die=True, stdOutput=True, errorOutput=True, force=False, actionshow=True)
            j.actions.add(sw, kwargs={"ipaddr": wicip}, die=True, stdOutput=True,
                          errorOutput=True, force=False, actionshow=True)

            # wic=self.get(wicip)
            # wics.append(wic)


class WIC(j.builder._BaseClass):
    """
    methods to work with console on windows
    """

    def __init__(self, ipaddr, passwd):
        """
        """
        JSBASE.__init__(self)
        from IPython import embed
        self._logger.debug("DEBUG NOW get prefab")
        embed()

        self._prefab

    def update(self):
        '''
        opkg update
        '''
        pass
