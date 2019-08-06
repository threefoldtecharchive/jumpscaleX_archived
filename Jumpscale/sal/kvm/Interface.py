from Jumpscale import j
import libvirt
from xml.etree import ElementTree
from sal.kvm.BaseKVMComponent import BaseKVMComponent
import random
import re


class Interface(BaseKVMComponent):
    """
    Object representation of xml portion of the interface in libvirt.
    """

    @staticmethod
    def generate_mac():
        """
        Generate mac address.
        """
        mac = [0x00, 0x16, 0x3E, random.randint(0x00, 0x7F), random.randint(0x00, 0xFF), random.randint(0x00, 0xFF)]
        return ":".join(map(lambda x: "%02x" % x, mac))

    def __init__(self, controller, bridge, name=None, mac=None, interface_rate=None, burst=None):
        """
        Interface object instance.

        @param controller object(j.sal.kvm.KVMController()): controller object to use.
        @param bridge object(j.sal.kvm.Network()): network object that create the bridge
        @param name str: name of interface
        @param mac str: mac address to be assigned to port
        @param interface_rate int: qos interface rate to bound to in Kb
        @param burst str: maximum allowed burst that can be reached in Kb/s
        """
        BaseKVMComponent.__init__(controller=controller)
        self.controller = controller
        self.name = name
        self.ovs = name is not None
        self.bridge = bridge
        self.qos = not (interface_rate is None)
        self.interface_rate = str(interface_rate)
        self.burst = burst
        if not (interface_rate is None) and burst is None:
            self.burst = str(int(interface_rate * 0.1))
        self.mac = mac if mac else Interface.generate_mac()
        self._ip = None
        self._iface = None

    def iface(self):
        if self._iface is None:
            self._iface = self.controller.connection.interfaceLookupByName(self.name)
        return self._iface

    @property
    def is_created(self):
        try:
            self.controller.connection.interfaceLookupByName(self.name)
            return True
        except libvirt.libvirtError as e:
            if e.get_error_code == libvirt.VIR_ERR_NO_INTERFACE:
                return False
            raise e

    @property
    def is_started(self):
        return self.iface.isActive() == 1

    def create(self, start=True, autostart=True):
        return NotImplementedError()

    def start(self, autostart=True):
        return NotImplementedError()

    def delete(self):
        """
        Delete interface and port related to certain machine.
        """
        if self.ovs:
            return self.controller.executor.execute("ovs-vsctl del-port %s %s" % (self.bridge.name, self.name))
        else:
            raise j.exceptions.NotImplemented("delete on non ovs network is not supported")

    def stop(self):
        return NotImplementedError()

    def to_xml(self):
        """
        Return libvirt's xml string representation of the interface.
        """
        Interfacexml = self.controller.get_template("interface.xml").render(
            macaddress=self.mac,
            bridge=self.bridge.name,
            qos=self.qos,
            rate=self.interface_rate,
            burst=self.burst,
            name=self.name,
        )
        return Interfacexml

    @classmethod
    def from_xml(cls, controller, xml):
        """
        Instantiate a interface object using the provided xml source and kvm controller object.

        @param controller object(j.sal.kvm.KVMController): controller object to use.
        @param xml str: xml string of machine to be created.
        """
        interface = ElementTree.fromstring(xml)
        if interface.find("virtualport") is None:
            name = None
        else:
            name = interface.find("virtualport").find("parameters").get("profileid")

        bridge_name = interface.find("source").get("bridge")
        bridge = j.sal.kvm.Network(controller, bridge_name)
        bandwidth = interface.findall("bandwidth")
        if bandwidth:
            interface_rate = bandwidth[0].find("inbound").get("average")
            burst = bandwidth[0].find("inbound").get("burst")
        else:
            interface_rate = burst = None
        mac = interface.find("mac").get("address")
        return cls(controller=controller, bridge=bridge, name=name, mac=mac, interface_rate=interface_rate, burst=burst)

    @classmethod
    def get_by_name(cls, controller, name):
        iface = interfaceLookupByName(name)
        return cls.from_xml(controller, iface.XMLDesc())

    @property
    def ip(self):
        if not self._ip:
            bridge_name = self.bridge.name
            mac = self.mac
            rc, ip, err = self.controller.executor.prefab.core.run(
                "nmap -n -sn $(ip r | grep %s | grep -v default | awk '{print $1}') | grep -iB 2 '%s' | head -n 1 | awk '{print $NF}'"
                % (bridge_name, mac)
            )
            ip_pat = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
            m = ip_pat.search(ip)
            if m:
                self._ip = m.group()
        return self._ip

    def qos(self, qos, burst=None):
        """
        Limit the throughtput into an interface as a for of qos.

        @interface str: name of interface to limit rate on
        @qos int: rate to be limited to in Kb
        @burst int: maximum allowed burst that can be reached in Kb/s
        """
        # TODO: *1 spec what is relevant for a vnic from QOS perspective, what can we do
        # goal is we can do this at runtime
        if self.ovs:
            self.controller.executor.execute("ovs-vsctl set interface %s ingress_policing_rate=%d" % (self.name, qos))
            if not burst:
                burst = int(qos * 0.1)
            self.controller.executor.execute(
                "ovs-vsctl set interface %s ingress_policing_burst=%d" % (self.name, burst)
            )
        else:
            raise j.exceptions.NotImplemented("qos for std bridge not implemeted")
