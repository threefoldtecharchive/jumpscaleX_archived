__author__ = "delandtj"
from Jumpscale import j
import os
import os.path
import subprocess
import sys
import time

command_name = sys.argv[0]

vsctl = "/usr/bin/ovs-vsctl"
ofctl = "/usr/bin/ovs-ofctl"
ip = "/sbin/ip"
ethtool = "/sbin/ethtool"
PHYSMTU = 2000

# TODO : errorhandling


def send_to_syslog(msg):
    pass
    # print msg
    # pid = os.getpid()
    # print ("%s[%d] - %s" % (command_name, pid, msg))
    # syslog.syslog("%s[%d] - %s" % (command_name, pid, msg))


def doexec(args):
    """Execute a subprocess, then return its return code, stdout and stderr"""
    send_to_syslog(args)
    proc = subprocess.Popen(
        args, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, bufsize=-1
    )
    rc = proc.wait()
    # rc = proc.communicate()
    stdout = proc.stdout
    stderr = proc.stderr
    return rc, stdout, stderr


def dobigexec(args):
    """Execute a subprocess, then return its return code, stdout and stderr"""
    send_to_syslog(args)
    proc = subprocess.Popen(
        args, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, bufsize=-1
    )
    rc = proc.communicate()
    return rc


def get_all_namespaces():
    cmd = "%s netns ls" % ip
    r, s, e = doexec(cmd.split())
    return [line.strip() for line in s.readlines()]


def get_all_ifaces():
    """
    List of network interfaces
    @rtype : dict
    """
    netpath = "/sys/class/net"
    ifaces = {}
    for i in os.listdir(netpath):
        addresspath = os.path.join(netpath, i, "address")
        if os.path.exists(addresspath):
            with open(addresspath) as f:
                addr = f.readline().strip()
                ifaces[i] = addr
    return ifaces


def get_all_bridges():
    cmd = "%s list-br" % vsctl
    r, s, e = doexec(cmd.split())
    l = [line.strip() for line in s.readlines()]
    return l


def ip_link_set(device, args):
    cmd = "ip l set " + device + " " + args
    doexec(cmd.split())


def limit_interface_rate(limit, interface, burst):
    cmd = "%s set interface %s ingress_policing_rate=%s"
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exception.RuntimeError(
            "Problem with setting rate on interface: %s , problem was : %s " % (interface, e)
        )
    cmd = "%s set interface %s ingress_policing_burst=%s"
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exception.RuntimeError(
            "Problem with setting burst on interface: %s , problem was : %s " % (interface, e)
        )


def createBridge(name):
    cmd = "%s --may-exist add-br %s" % (vsctl, name)
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exceptions.RuntimeError("Problem with creation of bridge %s, err was: %s" % (name, e))
    if name == "public":
        cmd = "%s set Bridge %s stp_enable=true" % (vsctl, name)
        r, s, e = doexec(cmd.split())
        if r:
            raise j.exceptions.RuntimeError("Problem setting STP on bridge %s, err was: %s" % (name, e))


def destroyBridge(name):
    cmd = "%s --if-exists del-br %s" % (vsctl, name)
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exceptions.RuntimeError("Problem with destruction of bridge %s, err was: %s" % (name, e))


def listBridgePorts(name):
    cmd = "%s list-ports %s" % (vsctl, name)
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exception.RuntimeError("Problem with listing of bridge %s's ports , err was: %s " % (name, e))
    return s.read()


def VlanPatch(parentbridge, vlanbridge, vlanid):
    parentpatchport = "%s-%s" % (vlanbridge, str(vlanid))
    bridgepatchport = "%s-%s" % (parentbridge, str(vlanid))
    cmd = "%s add-port %s %s tag=%s -- set Interface %s type=patch options:peer=%s" % (
        vsctl,
        parentbridge,
        parentpatchport,
        vlanid,
        parentpatchport,
        bridgepatchport,
    )
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exceptions.RuntimeError("Add extra vlan pair failed %s" % (e.readlines()))
    cmd = "%s add-port %s %s -- set Interface %s type=patch options:peer=%s" % (
        vsctl,
        vlanbridge,
        bridgepatchport,
        bridgepatchport,
        parentpatchport,
    )
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exceptions.RuntimeError("Add extra vlan pair failed %s" % (e.readlines()))


def addVlanPatch(parbr, vlbr, id, mtu=None):
    def bridge_exists(br):
        brexist = "{0} br-exists {1}".format(vsctl, br)
        r, s, e = doexec(brexist.split())
        return r == 0

    def port_exists(br, port):
        listprts = "{0} list-ports {1}".format(vsctl, br)
        r, s, e = doexec(listprts.split())
        return port in s.read()

    parport = "{}-{!s}".format(vlbr, id)
    brport = "{}-{!s}".format(parbr, id)
    if not bridge_exists(vlbr):
        brcreate = "{0} add-br {1}".format(vsctl, vlbr)
        r, s, e = doexec(brcreate.split())
    if not port_exists(vlbr, brport):
        addport = "{0} add-port {1} {3} -- set Interface {3} type=patch options:peer={2}".format(
            vsctl, vlbr, parport, brport
        )
        r, s, e = doexec(addport.split())
    if not port_exists(parbr, parport):
        c = "{4} add-port {0} {2} tag={3!s} -- set Interface {2} type=patch options:peer={1}".format(
            parbr, brport, parport, id, vsctl
        )
        r, s, e = doexec(c.split())
    if mtu:
        ip_link_set(vlbr, "mtu {0}".format(mtu))


def createNameSpace(name):
    if name not in get_all_namespaces():
        cmd = "%s netns add %s" % (ip, name)
        r, s, e = doexec(cmd.split())
    else:
        send_to_syslog("Namespace %s already exists, not creating" % name)


def destroyNameSpace(name):
    if name in get_all_namespaces():
        cmd = "%s netns delete %s" % (ip, name)
        r, s, e = doexec(cmd.split())
    else:
        send_to_syslog("Namespace %s doesn't exist, nothing done " % name)


def createVethPair(left, right):
    cmd = "%s link add %s type veth peer name %s" % (ip, left, right)
    allifaces = get_all_ifaces()
    if left in allifaces or right in allifaces:
        # one of them already exists
        send_to_syslog("Problem with creation of vet pair %s, %s :one of them exists" % (left, right))
    r, s, e = doexec(cmd.split())
    # wait for it to come up
    time.sleep(0.2)
    ip_link_set(left, "up")
    ip_link_set(right, "up")  # when sent into namespace, it'll be down again
    disable_ipv6(left)  # not right, as it can be used in a namespace


def destroyVethPair(left):
    cmd = "%s link del %s " % (ip, left)
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exceptions.RuntimeError("Problem with destruction of Veth pair %s, err was: %s" % (left, e))


def createVXlan(vxname, vxid, multicast, vxbackend):
    """
    Always brought up too
    Created with no protocol, and upped (no ipv4, no ipv6)
    Fixed standard : 239.0.x.x, id
    # 0000-fe99 for customer vxlans, ff00-ffff for environments
    MTU of VXLAN = 1500
    """
    cmd = "ip link add %s type vxlan id %s group %s ttl 60 dev %s" % (vxname, vxid, multicast, vxbackend)
    r, s, e = doexec(cmd.split())
    disable_ipv6(vxname)
    setMTU(vxname, 1500)
    ip_link_set(vxname, "up")
    if r:
        send_to_syslog("Problem with creation of vxlan %s, err was: %s" % (vxname, e.readlines()))


def destroyVXlan(name):
    cmd = "%s link del %s " % (ip, name)
    r, s, e = doexec(cmd.split())
    if r:
        send_to_syslog("Problem with destruction of Veth pair %s, err was: %s" % (name, e.readlines()))
        exit(1)


def addIPv4(interface, ipobj, namespace=None):
    netmask = ipobj.prefixlen
    ipv4addr = ipobj.ip
    # if ip existst on interface, we assume all ok

    if namespace is not None:
        cmd = "%s netns exec %s ip addr add %s/%s dev %s" % (ip, namespace, ipv4addr, netmask, interface)
    else:
        cmd = "%s addr add %s/%s dev %s" % (ip, ipv4addr, netmask, interface)
    r, s, e = doexec(cmd.split())
    if r:
        send_to_syslog("Could not add IP %s to interface %s " % (ipv4addr, interface))
    return r, e


def addIPv6(interface, ipobj, namespace=None):
    netmask = ipobj.prefixlen
    ipv6addr = ipobj.ip
    # if ip existst on interface, we assume all ok

    if namespace is not None and namespace in allnamespaces:
        cmd = "%s netns exec %s ip addr add %s/%s dev %s" % (ip, namespace, ipv6addr, netmask, interface)
    else:
        cmd = "%s addr add %s/%s dev %s" % (ip, ipv6addr, netmask, interface)
    r, s, e = doexec(cmd.split())
    if r:
        send_to_syslog("Could not add IP %s to interface %s " % (ipv6addr, interface))
    return r, e


def connectIfToBridge(bridge, interfaces):
    for interface in interfaces:
        cmd = "%s --if-exists del-port %s %s" % (vsctl, bridge, interface)
        r, s, e = doexec(cmd.split())
        cmd = "%s --may-exist add-port %s %s" % (vsctl, bridge, interface)
        r, s, e = doexec(cmd.split())
        if r:
            raise j.exceptions.RuntimeError("Error adding port %s to bridge %s" % (interface, bridge))


def removeIfFromBridge(bridge, interfaces):
    for interface in interfaces:
        cmd = "%s --if-exists del-port %s %s" % (vsctl, bridge, interface)
        r, s, e = doexec(cmd.split())
        if r:
            raise j.exceptions.RuntimeError("Error adding port %s to bridge %s" % (interface, bridge))


def connectIfToNameSpace(nsname, interface):
    cmd = "%s link set %s netns %s" % (ip, interface, nsname)
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exceptions.RuntimeError("Error moving %s to namespace %s" % (interface, nsname))


def disable_ipv6(interface):
    if interface in get_all_ifaces():
        cmd = "sysctl -w net.ipv6.conf.%s.disable_ipv6=1" % interface
        r, s, e = doexec(cmd.split())


def setMTU(interface, mtu):
    cmd = "ip link set %s mtu %s" % (interface, mtu)
    r, s, e = doexec(cmd.split())
    if r:
        raise j.exceptions.RuntimeError("Could not set %s to MTU %s" % (interface, mtu))


def addBond(bridge, bondname, iflist, lacp="active", lacp_time="fast", mode="balance-tcp", trunks=None):
    # bond_mode=balance-tcp lacp=active bond_fake_iface=false
    # other_config:lacp-time=fast bond_updelay=2000 bond_downdelay=400
    """
    Add a bond to a bridge
    :param bridge: BridgeName (string)
    :param bondname: Bondname (string)
    :param iflist: list or tuple
    :param lacp: "active" or "passive"
    :param lacp_time: mode "fast" or "slow"
    :param mode: balance-tcp, balance-slb, active-passive
    :param trunks: allowed VLANS (list or tuple)
    """

    intf = re.split("\W+", iflist)
    if isinstance(trunks, str):
        tr = re.split("\W+", trunks)
    buildup = "add-bond %s %s " % (bridge, bondname) + " ".join(e for e in list(set(intf))) + " lacp=%s " % lacp
    buildup = buildup + " -- set Port %s bond_mode=%s bond_fake_iface=false " % (bondname, mode)
    buildup = buildup + "other_config:lacp-time=%s bond_updelay=2000 bond_downdelay=400 " % lacp_time
    if trunks is not None:
        trlist = ",".join(str(e) for e in list(set(tr)))
        buildup = buildup + "trunks=" + trlist
    # no use to autoconf ipv6, as this won't work anyway
    for i in iflist:
        disable_ipv6(i)
    r, s, e = doexec(buildup.split())
    if e:
        raise j.exceptions.RuntimeError("Could not create bond %s for bridge %s" % (bondname, bridge))
