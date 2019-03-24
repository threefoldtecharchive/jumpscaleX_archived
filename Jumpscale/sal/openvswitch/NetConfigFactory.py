#!/usr/bin/env python
import netaddr
import pprint

from Jumpscale import j
from .VXNet import vxlan as vxlan
from .VXNet import netclasses as netcl
from .VXNet.utils import *

JSBASE = j.application.JSBaseClass


class NetConfigFactory(j.application.JSBaseClass):

    def __init__(self):
        self.__jslocation__ = "j.sal.openvswitch"
        self._layout = None
        self.PHYSMTU = 2000  # will fit all switches
        self._executor = j.tools.executorLocal
        self.netcl = netcl
        JSBASE.__init__(self)

    def getConfigFromSystem(self, reload=False):
        """
        walk over system and get configuration, result is dict
        """
        if self._layout is None or reload:
            self._layout = vxlan.NetLayout()
            self._layout.load()
        # add_ips_to(self._layout)  #TODO: fix
        return self._layout.nicdetail

    def _exec(self, cmd, failOnError=True):
        self._log_debug(cmd)
        rc, out = self._executor.execute(cmd, die=failOnError)
        return out

    def removeOldConfig(self):
        cmd = "brctl show"
        for line in self._exec(cmd).split("\n"):
            if line.strip() == "" or line.find("bridge name") != -1:
                continue
            name = line.split("\t")[0]
            self._exec("ip link set %s down" % name)
            self._exec("brctl delbr %s" % name)

        for intname, data in list(self.getConfigFromSystem(reload=True).items()):
            if "PHYS" in data["detail"]:
                continue
            if intname == "ovs-system":
                continue
            self._exec("ovs-vsctl del-br %s" % intname, False)

        out = self._exec("virsh net-list", False)
        if out.find("virsh: not found") == -1:
            state = "start"
            for line in out.split("\n"):
                if state == "found":
                    if line.strip() == "":
                        continue
                    line = line.replace("\t", " ")
                    name = line.split(" ")[0]
                    self._exec("virsh net-destroy %s" % name, False)
                    self._exec("virsh net-undefine %s" % name, False)

                if line.find("----") != -1:
                    state = "found"

        j.tools.path.get("/etc/default/lxc-net").write_text("USE_LXC_BRIDGE=\"false\"",
                                                            append=True)  # TODO: UGLY use editor !!!

        # Not used and expensive self.getConfigFromSystem(reload=True)

        j.tools.path.get("/etc/network/interfaces").write_text("auto lo\n iface lo inet loopback\n\n")

    def initNetworkInterfaces(self):
        """
        Resets /etc/network/interfaces with a basic configuration
        """
        j.tools.path.get("/etc/network/interfaces").write_text("auto lo\n iface lo inet loopback\n\n")

    def printConfigFromSystem(self):
        pprint.pprint(self.getConfigFromSystem())

    def newBridge(self, name, interface=None):
        """
        @param interface ['interface'] can take multiple interfaces where to connect this bridge
        """
        br = netcl.Bridge(name)
        br.create()
        if interface is not None:
            br.connect(interface)

    def vnicQOS(self, limit, interface, burst_limit=None):
        """
        @param limit apply Qos policing to limit the rate throught a
        @param burst_limit most the maximum amount of data (in Kb) that
               this interface can send beyond the policing rate.default to 10% of rate
        """
        if not burst_limit:
            burst_limit = 0.1 * limit
        netcl.limit_interface_rate(limit, interface, burst_limit)

    def newVlanBridge(self, name, parentbridge, vlanid, mtu=None):
        addVlanPatch(parentbridge, name, vlanid, mtu=mtu)

    def ensureVXNet(self, networkid, backend):
        vxnet = vxlan.VXNet(networkid, backend)
        vxnet.innamespace = False
        vxnet.inbridge = True
        vxnet.apply()
        return vxnet

    def createVXLanBridge(self, networkid, backend, bridgename=None):
        """
        Creates a proper vxlan interface and bridge based on a backplane
        """
        networkoid = netcl.NetID(networkid)
        vxlan = netcl.VXlan(networkoid, backend)
        vxlan.create()
        vxlan.no6()
        bridge = netcl.Bridge(bridgename)
        bridge.create()
        bridge.connect(vxlan.name)
        return vxlan

    def getType(self, interfaceName):
        layout = self.getConfigFromSystem()
        if interfaceName not in layout:
            raise j.exceptions.RuntimeError("cannot find interface %s" % interfaceName)
        interf = layout[interfaceName]
        if "type" in interf["params"]:
            return interf["params"]["type"]
        return None

    def setBackplaneDhcp(self, interfacename="eth0", backplanename="Public"):
        """
        DANGEROUS, will remove old configuration
        """
        C = """
auto $BPNAME
allow-ovs $BPNAME
iface $BPNAME inet dhcp
 dns-nameserver 8.8.8.8 8.8.4.4
 ovs_type OVSBridge
 ovs_ports $iname

allow-$BPNAME $iname
iface $iname inet manual
 ovs_bridge $BPNAME
 ovs_type OVSPort
 up ip link set $iname mtu $MTU
"""
        C = C.replace("$BPNAME", str(backplanename))
        C = C.replace("$iname", interfacename)
        C = C.replace("$MTU", str(self.PHYSMTU))

        ed = j.tools.code.getTextFileEditor("/etc/network/interfaces")
        ed.setSection(backplanename, C)

    def setBackplaneNoAddress(self, interfacename="eth0", backplanename=1):
        """
        DANGEROUS, will remove old configuration
        """
        C = """
auto $BPNAME
allow-ovs $BPNAME
iface $BPNAME inet manual
  ovs_type OVSBridge
  ovs_ports eth7

allow-$BPNAME $iname
iface $iname inet manual
  ovs_bridge $BPNAME
  ovs_type OVSPort
  up ip link set $iname mtu $MTU
"""
        C = C.replace("$BPNAME", str(backplanename))
        C = C.replace("$iname", interfacename)
        C = C.replace("$MTU", str(self.PHYSMTU))  # strings here
        ed = j.tools.code.getTextFileEditor("/etc/network/interfaces")
        ed.setSection(backplanename, C)

    def configureStaticAddress(self, interfacename="eth0", ipaddr="192.168.10.10/24", gw=None):
        """
        Configure a static address
        """
        C = """
auto $interface
allow-ovs $interface
iface $interface inet static
 address $ipbase
 netmask $mask
 $gw
"""
        n = netaddr.IPNetwork(ipaddr)

        C = C.replace("$interface", interfacename)
        C = C.replace("$ipbase", str(n.ip))
        C = C.replace("$mask", str(n.netmask))
        if gw:
            C = C.replace("$gw", "gateway %s" % gw)
        else:
            C = C.replace("$gw", "")

        ed = j.tools.code.getTextFileEditor("/etc/network/interfaces")
        ed.setSection(interfacename, C)
        ed.save()

    def setBackplaneNoAddressWithBond(self, bondname, bondinterfaces, backplanename='backplane'):
        """
        DANGEROUS, will remove old configuration
        """
        C = """
auto $BPNAME
allow-ovs $BPNAME
iface $BPNAME inet manual
 ovs_type OVSBridge
 ovs_ports $bondname

allow-$BPNAME $bondname
iface $bondname inet manual
 ovs_bridge $BPNAME
 ovs_type OVSBond
 ovs_bonds $bondinterfaces
 ovs_options bond_mode=balance-tcp lacp=active bond_fake_iface=false other_config:lacp-time=fast bond_updelay=2000 bond_downdelay=400
 $disable_ipv6
"""
        interfaces = ''
        disable_ipv6 = ''
        for interface in bondinterfaces:
            interfaces += '%s ' % interface
            disable_ipv6 += 'pre-up ip l set %s mtu 2000 \n up sysctl -w net.ipv6.conf.%s.disable_ipv6=1 \n' % (
                interface, interface)
        C = C.replace("$BPNAME", str(backplanename))
        C = C.replace("$bondname", bondname)
        C = C.replace("$MTU", str(self.PHYSMTU))
        C = C.replace("$bondinterfaces", interfaces)
        C = C.replace("$disable_ipv6", disable_ipv6)

        ed = j.tools.code.getTextFileEditor("/etc/network/interfaces")
        ed.setSection(backplanename, C)
        ed.save()

    def setBackplane(self, interfacename="eth0", backplanename=1, ipaddr="192.168.10.10/24", gw=""):
        """
        DANGEROUS, will remove old configuration
        """
        C = """
auto $BPNAME
allow-ovs $BPNAME
iface $BPNAME inet static
 address $ipbase
 netmask $mask
 dns-nameserver 8.8.8.8 8.8.4.4
 ovs_type OVSBridge
 ovs_ports $iname
 $gw

allow-$BPNAME $iname
iface $iname inet manual
 ovs_bridge $BPNAME
 ovs_type OVSPort
 up ip link set $iname mtu $MTU
"""
        n = netaddr.IPNetwork(ipaddr)
        C = C.replace("$BPNAME", str(backplanename))
        C = C.replace("$iname", interfacename)
        C = C.replace("$ipbase", str(n.ip))
        C = C.replace("$mask", str(n.netmask))
        C = C.replace("$MTU", str(self.PHYSMTU))
        if gw != "" and gw is not None:
            C = C.replace("$gw", "gateway %s" % gw)
        else:
            C = C.replace("$gw", "")

        ed = j.tools.code.getTextFileEditor("/etc/network/interfaces")
        ed.setSection(backplanename, C)
        ed.save()

    def setBackplaneWithBond(self, bondname, bondinterfaces, backplanename='backplane',
                             ipaddr="192.168.10.10/24", gw=""):
        """
        DANGEROUS, will remove old configuration
        """
        C = """
auto $BPNAME
allow-ovs $BPNAME
iface $BPNAME inet static
 address $ipbase
 netmask $mask
 dns-nameserver 8.8.8.8 8.8.4.4
 ovs_type OVSBridge
 ovs_ports $bondname
 $gw

allow-$BPNAME $bondname
iface $bondname inet manual
 ovs_bridge $BPNAME
 ovs_type OVSBond
 ovs_bonds $bondinterfaces
 ovs_options bond_mode=balance-tcp lacp=active bond_fake_iface=false other_config:lacp-time=fast bond_updelay=2000 bond_downdelay=400
 $disable_ipv6
"""
        n = netaddr.IPNetwork(ipaddr)
        interfaces = ''
        disable_ipv6 = ''
        for interface in bondinterfaces:
            interfaces += '%s ' % interface
            disable_ipv6 += 'pre-up ip l set %s mtu 2000 \n up sysctl -w net.ipv6.conf.%s.disable_ipv6=1 \n' % (
                interface, interface)
        C = C.replace("$BPNAME", str(backplanename))
        C = C.replace("$bondname", bondname)
        C = C.replace("$ipbase", str(n.ip))
        C = C.replace("$mask", str(n.netmask))
        C = C.replace("$MTU", str(self.PHYSMTU))
        if gw != "" and gw is not None:
            C = C.replace("$gw", "gateway %s" % gw)
        else:
            C = C.replace("$gw", "")
        C = C.replace("$bondinterfaces", interfaces)
        C = C.replace("$disable_ipv6", disable_ipv6)

        ed = j.tools.code.getTextFileEditor("/etc/network/interfaces")
        ed.setSection(backplanename, C)
        ed.save()

    def applyconfig(self, interfacenameToExclude=None, backplanename=None):
        """
        DANGEROUS, will remove old configuration
        """
        for intname, data in list(self.getConfigFromSystem(reload=True).items()):
            if "PHYS" in data["detail"] and intname != interfacenameToExclude:
                self._exec("ip addr flush dev %s" % intname, False)
                self._exec("ip link set %s down" % intname, False)

        if backplanename is not None:
            self._exec("ifdown %s" % backplanename, failOnError=False)
            # self._exec("ifup %s"%backplanename, failOnError=True)

        # TODO: need to do more checks here that it came up and retry couple of times if it did not
        #@ can do this by investigating self.getConfigFromSystem

        self._executor.execute("/etc/init.d/openvswitch-switch restart")

        self._log_debug((self._exec("ip a", failOnError=True)))
        self._log_debug((self._exec("ovs-vsctl show", failOnError=True)))

    def newBondedBackplane(self, name, interfaces, trunks=None):
        """
        Reasonable defaults  : mode=balance-tcp, lacp=active,fast, bondname=brname-Bond, all vlans allowed
        """
        br = netcl.BondBridge(name, interfaces)
        br.create()
