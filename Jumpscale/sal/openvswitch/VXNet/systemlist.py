__author__ = "delandtj"

from .utils import *
import fcntl
import re
from netaddr import *


def acquire_lock(path):
    """
        little tool to do EAGAIN until lockfile released
    :param path:
    :return: path
    """
    lock_file = open(path, "w")
    while True:
        send_to_syslog("attempting to acquire lock %s" % path)
        try:
            fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            send_to_syslog("acquired lock %s" % path)
            return lock_file
        except IOError as e:
            send_to_syslog("failed to acquire lock %s because '%s' - waiting 1 second" % (path, e))
            time.sleep(1)


def wait_for_if(interface):
    pass


def pprint_dict(a):
    from pprint import pprint

    pprint(dict(list(a.items())))


def get_nic_params():
    nictypes = {}
    bridges = get_all_bridges()
    namespaces = get_all_namespaces()

    def populatenictypes(lines, namespace=None):
        for l in lines:
            if "state" not in l:
                continue
            entry = l.strip().split()
            intf = entry[1].rstrip(":")
            if intf == "lo":
                continue
            nictypes[intf] = {}
            if "vxlan" in entry:
                want = ("state", "id", "mtu", "id", "group", "dev", "port")
                params = parse_ipl_line(entry, want)
                params["type"] = "vxlan"
            elif "veth" in entry:
                want = ("state", "id", "mtu")
                params = parse_ipl_line(entry, want)
                params["peer"] = find_veth_peer(intf, ns=namespace)
                params["type"] = "veth"
            elif "tun" in entry:
                want = ("state", "id", "mtu")
                params = parse_ipl_line(entry, want)
                params["type"] = "tun"
            elif intf in bridges:
                want = ("state", "id", "mtu")
                params = parse_ipl_line(entry, want)
                params["type"] = "bridge"
            else:
                want = ("state", "id", "mtu")
                params = parse_ipl_line(entry, want)
            nictypes[intf]["params"] = params
            if namespace is None:
                nictypes[intf]["detail"] = get_nic_detail(intf)
                nictypes[intf]["namespace"] = None
            else:
                nictypes[intf]["namespace"] = namespace

        return nictypes

    # local
    cmd = "%s -o -d link show " % ip
    intflist = dobigexec(cmd.split())
    lines = intflist[0].decode().splitlines()
    nictypes = populatenictypes(lines)
    # all namespaces
    for ns in namespaces:
        cmd = "%s netns exec %s %s -o -d link show" % (ip, ns, ip)
        (r, s, e) = doexec(cmd.split())
        lines = s.readlines()
        nictypes = dict(list(populatenictypes(lines, namespace=ns).items()) + list(nictypes.items()))
    return nictypes


def parse_ipl_line(line, params):
    """
    Get NIC settings in line
    :param line: list of ip -o -d link show
    :param params: tuple of keywords
    """
    nicsettings = {}
    for p in params:
        if p == "state":
            nicsettings[p] = line[2].lstrip("<").rstrip(">").split(",")
        elif p == "id":
            nicsettings[p] = line[0].rstrip(":")
        else:
            nicsettings[p] = line[line.index(p) + 1]  # watch out for index out of range
    return nicsettings


def get_nic_detail(interface):
    prefix = "/sys/class/net"
    # every interface has a mac
    carrier = None
    speed = None
    peer = None

    # TODO *2 Should it give errors if paths don't exist?
    addr = ""
    if os.path.exists(os.path.join(prefix, interface, "address")):
        with open(os.path.join(prefix, interface, "address")) as f:
            addr = f.readline().strip()
    # if linked to somewhere in pci it prolly is physical
    typ = "UNKNOWN"
    if os.path.exists(os.path.join(prefix, interface)):
        if "pci" in os.readlink(os.path.join(prefix, interface)):
            typ = "PHYS"
        elif "virtual" in os.readlink(os.path.join(prefix, interface)):
            typ = "VIRT"

    if typ == "PHYS":
        # verify if link has carrier
        (r, s, e) = doexec(["ethtool", interface])
        # Link Detected and  speed
        out = s.readlines()
        for i in out:
            string = i.strip().split(":")
            if string[0] == "Link detected":
                carrier = True if string[1].strip() == "yes" else False
        if carrier:
            for i in out:
                string = i.strip().split(":")
                if string[0] == "Speed":
                    speed = string[1].strip()
    return [typ, addr, carrier, speed]


def find_veth_peer(interface, ns=None):
    """
    Left or right part of veth
    @param interface:
    @return: name
    """
    cmd = "%s -S %s" % (ethtool, interface)
    if ns is not None:
        cmd = "%s netns exec %s " % (ip, ns) + cmd
    r, s, e = doexec(cmd.split())
    a = s.readlines()
    peer = [int(x.split(":")[1].rstrip()) for x in a if "ifindex" in x]
    if len(peer) > 0:
        return peer[0]
    else:
        return None


def add_ips_to(physlayout):
    fullset = {}
    iplist = get_ip_addrs()
    for key in iplist:  # you can have interfaces without ip
        fullset[key] = physlayout[key]
        fullset[key]["ipaddrs"] = iplist[key]
    # merge rest
    for key in physlayout:
        if key not in fullset:
            fullset[key] = physlayout[key]
        if physlayout[key]["namespace"] is not None:
            fullset[key]["ipaddrs"] = get_ip_addrs(namespace=physlayout[key]["namespace"])
    return fullset


def get_ip_addrs(onlypermanent=False, namespace=None):
    if namespace is None:
        cmd = "%s -o addr show" % ip
    else:
        cmd = "%s netns exec %s %s -o addr show" % (ip, namespace, ip)
    (r, s, e) = doexec(cmd.split())
    lines = s.readlines()
    iplist = {}
    for l in lines:
        i = l.strip().split()
        if "forever" not in l and onlypermanent:
            continue
        iface = i[1].rstrip(":")
        ipstr = i[3]
        if iface == "lo":
            continue
        ipobj = IPNetwork(ipstr)
        if iface not in iplist:
            iplist[iface] = {}
            iplist[iface]["ipaddrs"] = []
            iplist[iface]["ipaddrs"].append(ipobj)
        else:
            iplist[iface]["ipaddrs"].append(ipobj)
    return iplist


def isup(interface):
    cmd = "%s -o link show dev %s" % interface
    r, s, e = doexec(cmd.split())
    line = s.readlines()
    l = line[0].strip().split()
    state = l[2].lstrip("<").rstrip(">").split(",")
    if "UP" in state:
        return True
    return False


def getnetworkstructure(onlypermanent=True, without_ip=False):
    """

    @param onlypermanent:
    @param without_ip:
    @return:
    """
    (r, s, e) = doexec("ip -o addr show".split())
    interfaces = s.readlines()
    s = {}
    for l in interfaces:
        i = l.split()
        if "forever" not in l and onlypermanent and not without_ip:
            continue
        id = re.match("\d+", i[0]).group()
        intf = i[1]
        inet = i[2]
        ipstr = i[3]
        if intf not in s:
            s[intf] = {}
        s[intf]["id"] = id
        if inet not in s[intf]:
            s[intf][inet] = []
        s[intf][inet].append(IPNetwork(ipstr))
        nictype, mac, carrier, speed = get_nic_detail(intf)
        s[intf]["nictype"] = nictype
        s[intf]["mac"] = mac
        if carrier:
            s[intf]["link"] = "detected"
            s[intf]["speed"] = speed
    return s


def cleanup_flows(bridge_name, interface):
    """
    flows of which ports do not exist any more get removed (generic cleanup)
    @param bridge_name:
    """
    flowports = list_ports_in_of()
    activeports = [int(get_vswitch_port(x)) for x in list_ports(interface)]
    ap = set(activeports)
    todelete = [x for x in flowports if x not in ap]
    for i in todelete:
        clear_vswitch_rules(bridge_name, i)


def list_ports_in_of(interface):
    """
    list ports in openFlow models
    @return:
    """
    ipm = re.compile("(?<=in_port\=)\d{1,5}")
    cmd = ofctl + " dump-flows " + interface
    (r, s, e) = doexec(cmd.split())
    li = [line.strip() for line in s.readlines() if "in_port" in line]
    ports = [int(ipm.search(x).group(0)) for x in li]
    return ports


def get_attached_mac_port(virt_vif):
    """
    @param virt_vif:
    @return: port and mac
    """
    if virt_vif:
        cmd = vsctl + " -f table -d bare --no-heading -- --columns=ofport,external_ids list Interface " + virt_vif
        (r, s, e) = doexec(cmd.split())
        o = s.readline().split()
        port = o.pop(0)
        mac = o.pop(0).split("=")[1]
        return port, mac
    else:
        send_to_syslog("No matching virt port found in get_attached_mac_port(virt_vif)")
        sys.exit(0)


def get_bridge_name(vif_name):
    """
    @param vif_name:
    @return: bridge
    """
    (rc, stdout, stderr) = doexec([vsctl, "port-to-br", vif_name])
    return stdout.readline().strip()


def list_ports(bridge_name):
    """
    @param bridge_name:
    @return: all ports on bridge
    """
    (rc, stdout, stderr) = doexec([vsctl, "list-ports", bridge_name])
    ports = [line.strip() for line in stdout.readlines()]
    return ports


def get_vswitch_port(vif_name):
    """
    @param vif_name:
    @return: all ports
    """
    (rc, stdout, stderr) = doexec([vsctl, "get", "interface", vif_name, "ofport"])
    return stdout.readline().strip()


def clear_vswitch_rules(bridge_name, port):
    """
    @param bridge_name:
    @param port:
    """
    doexec([ofctl, "del-flows", bridge_name, "in_port=%s" % port])


if __name__ == "__main__":
    a = get_nic_params()
    pprint_dict(a)
