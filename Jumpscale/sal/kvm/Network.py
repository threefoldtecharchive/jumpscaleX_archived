from xml.etree import ElementTree
import libvirt
from sal.kvm.BaseKVMComponent import BaseKVMComponent


class Network(BaseKVMComponent):
    """Network object representation of xml and actual Network."""

    def __init__(self, controller, name, bridge=None, interfaces=[], ovs=True):
        """
        Instance of network object representation of open vstorage network.

        @param controller object: connection to libvirt controller.
        @param name string: name of network.
        @param bridge string: bridge name. if empty use the self.name as bridge name
        @param interfaces list: interfaces list.
        @param ovs boolean: use ovs to create bridge. if False use ip commands
        """
        BaseKVMComponent.__init__(controller=controller)
        self.name = name
        self.ovs = ovs
        self.bridge = bridge if bridge else name
        self._interfaces = interfaces
        self.controller = controller
        self._nw = None

    @property
    def nw(self):
        """
        underlying libvirt network object
        """
        if not self._nw:
            self._nw = self.controller.connection.networkLookupByName(self.name)
        return self._nw

    @property
    def interfaces(self):
        """
        Return list of interfaces names added to the bridge of the current network
        """
        if self._interfaces is None:
            if self.bridge in self.controller.executor.execute("ovs-vsctl list-br"):
                self._interfaces = self.controller.executor.execute("ovs-vsctl list-ports %s" % self.bridge)
            else:
                return []
        return self._interfaces

    @property
    def is_created(self):
        try:
            self.controller.connection.networkLookupByName(self.name)
            return True
        except libvirt.libvirtError as e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_NETWORK:
                return False
            raise e

    @property
    def is_started(self):
        return self.nw.isActive() == 1

    def create(self, start=True, autostart=True):
        """
        @param start bool: will start the network after creating it
        @param autostart bool: will autostart Network on host boot
        create and start network
        """
        nics = [interface for interface in self.interfaces]
        if self.ovs:
            self.controller.executor.execute("ovs-vsctl --may-exist add-br %s" % self.name)
            self.controller.executor.execute("ovs-vsctl set Bridge %s stp_enable=true" % self.name)
            for nic in nics:
                self.controller.executor.execute("ovs-vsctl --may-exist add-port %s %s" % (self.name, nic))

        else:
            self.controller.executor.execute("ip link add %s type bridge" % self.name)
            for nic in nics:
                self.controller.executor.execute("ip link set %s master %s" % (nic, self.name))

        self.controller.connection.networkDefineXML(self.to_xml())

        if start:
            self.start()

        if autostart:
            self.nw.setAutostart(1)
        else:
            self.nw.setAutostart(0)

    def start(self, autostart=True):
        """
        start a (previously defined) inactive network
        @param autostart bool: set autostart flag.
        """
        if self.ovs:
            pass
        else:
            self.controller.executor.execute("ip link set %s up" % (self.name))

        if autostart:
            self.nw.setAutostart(1)
        else:
            self.nw.setAutostart(0)

        if not self.is_started:
            self.nw.create()

    def delete(self):
        """
        Delete the network.
        """
        self.stop()

        if self.ovs:
            self.controller.executor.execute("ovs-vsctl --if-exists del-br %s" % self.name)
        else:
            self.controller.executor.execute("ip link delete %s" % self.name)

        self.nw.undefine()

    def stop(self):
        if self.is_started:
            self.nw.destroy()

    def to_xml(self):
        """
        Return libvirt's xml string representation of the Network.
        """
        networkxml = self.controller.get_template("network.xml").render(networkname=self.name, bridge=self.bridge)
        return networkxml

    @classmethod
    def from_xml(cls, controller, source):
        """
        Instantiate a Network object using the provided xml source and kvm controller object.

        @param controller object(j.sal.kvm.KVMController): controller object to use.
        @param source  str: xml string of machine to be created.
        """
        network = ElementTree.fromstring(source)
        name = network.findtext("name")
        bridge = network.findall("bridge")[0].get("name")
        rc, _, _ = controller.executor.execute("ovs-vsctl br-exists %s" % name, die=False)
        ovs = rc == 0
        return cls(controller, name, bridge, None, ovs=ovs)

    @classmethod
    def get_by_name(cls, controller, name):
        nw = controller.connection.networkLookupByName(name)
        return cls.from_xml(controller, nw.XMLDesc())
