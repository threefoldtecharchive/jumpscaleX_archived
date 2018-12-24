__author__ = 'delandtj'

from netaddr import *
from .netclasses import *
from .systemlist import *
from Jumpscale import j

JSBASE = j.application.JSBaseClass

command_name = sys.argv[0]


class NetLayout(j.builder._BaseClass):

    def __init__(self):
        self.interfaces = get_all_ifaces()
        self.nicdetail = {}
        self.bridges = {}
        JSBASE.__init__(self)

    def load(self):
        self.nicdetail = get_nic_params()

    def reload(self):
        self.load()

    def is_phys(self, interface):
        if 'PHYS' in self.nicdetail[interface]['detail']:
            return True
        return False

    def has_ip(self, interface, ipnetobj):
        for i in self.nicdetail[interface]['ipaddr']:
            if ipnetobj.ip == i.ip:
                return True
        return False

    def exist_ip(self, ipobj):
        for interface in self.nicdetail:
            if self.nicdetail[interface]['ipaddr'].ip == ipobj.ip:
                return True
        return False

    def exist_interface(self, interface):
        if interface in self.interfaces:
            return True
        return False


class VXNet(j.builder._BaseClass):

    def __init__(self, netid, backend='vxbackend'):
        self.netid = NetID(netid)
        self.ipv6 = None
        self.ipv4 = None
        self.backend = backend
        self.existing = NetLayout()
        JSBASE.__init__(self)

    def apply(self):
        """
        ethpairs : left always to bridge, right to namespace
        """
        self.existing.load()
        if self.innamespace:
            # IP in Namespace
            vxlan = VXlan(self.netid, self.backend)
            if vxlan.name in self.existing.nicdetail:
                send_to_syslog('VXLan %s exists, not creating' % vxlan.name)
            else:
                vxlan.create()
                vxlan.no6()

            bridge = VXBridge(self.netid)
            self.bridge = bridge
            if bridge.name in self.existing.nicdetail:
                send_to_syslog('Bridge %s exists, not creating' % bridge.name)
            else:
                bridge.create()
                bridge.no6()
                bridge.connect(vxlan.name)

            namespace = VXNameSpace(self.netid)
            if namespace.name in self.existing.nicdetail:
                send_to_syslog('NameSpace %s exists, not creating' % namespace.name)
            else:
                namespace.create()
            veth = VethPair(self.netid)
            veth.create()
            bridge.connect(veth.left)
            namespace.connect(veth.right)
            addIPv4(veth.right, self.ipv4, namespace=namespace.name)
            if self.ipv6 is not None:
                addIPv6(veth.right, self.ipv6, namespace=namespace.name)
        elif self.inbridge:
            # IP on bridge
            vxlan = VXlan(self.netid, self.backend)
            vxlan.create()
            vxlan.no6()
            bridge = VXBridge(self.netid)
            self.bridge = bridge
            bridge.create()
            bridge.connect(vxlan.name)
            if self.ipv4 is not None:
                addIPv4(bridge.name, self.ipv4)
            if self.ipv6 is not None:
                addIPv6(bridge.name, self.ipv6)
        else:
            # no bridge, no namespace, just IP
            vxlan = VXlan(self.netid, self.backend)
            vxlan.create()
            addIPv4(vxlan.name, self.ipv4)
            addIPv6(vxlan.name, self.ipv6)

    def rebuild(self, netid):
        # destroy all connected with id
        pass

    def destroy(self, netid):
        # destroy all connected with id
        pass
