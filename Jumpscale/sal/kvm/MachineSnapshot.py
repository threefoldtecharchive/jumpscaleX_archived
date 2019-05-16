from xml.etree import ElementTree
from Jumpscale import j
from sal.kvm.BaseKVMComponent import BaseKVMComponent


class MachineSnapshot(BaseKVMComponent):
    def __init__(self, controller, domain, name, description=""):
        BaseKVMComponent.__init__(controller=controller)
        self.controller = controller
        self.domain = domain
        self.name = name
        self.description = description

    @classmethod
    def from_xml(cls, controller, source):
        snapshot = ElementTree.fromstring(source)
        description = snapshot.findtext("description")
        name = snapshot.findtext("name")
        domain_uuid = snapshot.findall("domain")[0].findtext("uuid")
        domain = controller.connection.lookupByUUIDString(domain_uuid)
        return MachineSnapshot(controller, domain, name, description)

    def to_xml(self):
        snapxml = self.controller.get_template("snapshot.xml").render(description=self.description, name=self.name)
        return snapxml

    def create(self):
        snapxml = self.to_xml()
        xml = self.domain.snapshotCreateXML(snapxml)
        return xml
