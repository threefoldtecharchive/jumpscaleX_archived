from Jumpscale import j

#
import re
import netaddr

# class NetworkingErro(Exception):
#     pass
JSBASE = j.application.JSBaseClass


class NetworkingError(Exception, JSBASE):
    def __init__(self, msg=""):
        JSBASE.__init__(self)
        self._log_error(msg)


class UnixNetworkManager(j.application.JSBaseClass):
    def __init__(self):
        self.__jslocation__ = "j.sal.nic"
        JSBASE.__init__(self)
        self._executor = j.tools.executorLocal
        self._nics = None

    def _nicExists(self, nic):
        if nic not in self.nics:
            raise NetworkingError("NIC doesn't exist")

    def configSet(self):
        contentConfig = "source /etc/network/interfaces.d/*\n"
        j.tools.path.get("/etc/network/interfaces").write_text(contentConfig)

    def ipGet(self, device):
        """
        Get IP of devie
        Result (ip, netmask, gateway)
        """
        self._nicExists(device)
        cmd = 'echo `ip a | grep %s | sed -n 2p | xargs | cut -d " " -f 2`' % device
        _, res, _ = self._executor.execute(cmd)
        ipmask = netaddr.IPNetwork(res)
        netmask = str(ipmask.netmask)
        ip = str(ipmask.ip)
        return (ip, netmask)

    def ipSet(self, device, ip=None, netmask=None, gw=None, inet="dhcp", commit=False):
        """
        Return all interfaces that has this ifname
        """
        self._nicExists(device)

        if inet not in ["static", "dhcp"]:
            raise j.exceptions.Value("Invalid inet .. use either dhcp or static")

        if inet == "static" and (not ip or not netmask):
            raise j.exceptions.Value("ip, and netmask, are required in static inet.")

        file = j.tools.path.get("/etc/network/interfaces.d/%s" % device)
        content = "auto %s\n" % device

        if inet == "dhcp":
            content += "iface %s inet dhcp\n" % device
        else:
            content += "iface %s inet static\naddress %s\nnetmask %s\n" % (device, ip, netmask)
            if gw:
                content += "gateway %s\n" % gw

        file.write_text(content)

        if commit:
            self.commit(device)
        else:
            self._log_info("Do NOT FORGET TO COMMIT")

    def ipReset(self, device, commit=False):
        self._nicExists(device)
        file = j.tools.path.get("/etc/network/interfaces.d/%s" % device)
        file.write_text("")

        if commit:
            self.commit()
        else:
            self._log_info("Do NOT FORGET TO COMMIT")

    @property
    def nics(self):
        if self._nics is None:
            _, ifaces, _ = self._executor.execute("""ifconfig -a | sed 's/[ \t].*//;/^$/d'""")
            self._nics = [iface for iface in ifaces.splitlines() if iface]

        self._nics = [nic.replace(":", "") for nic in self._nics]
        return self._nics

    def commit(self, device=None):
        # - make sure loopback exist
        self.configSet()
        content = "auto lo\niface lo inet loopback\n"
        j.tools.path.get("/etc/network/interfaces.d/lo").write_text(content)
        if device:
            self._log_info("Restarting interface %s" % device)
            (ip, _) = self.ipGet(device)
            self._executor.execute("ip a del %s dev %s" % (ip, device))
        self._executor.execute("systemctl restart networking")
        self._log_info("DONE")
