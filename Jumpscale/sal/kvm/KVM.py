from Jumpscale import j
from JumpscaleLib.sal.kvm.Network import Network
from JumpscaleLib.sal.kvm.Interface import Interface
from JumpscaleLib.sal.kvm.Disk import Disk
from JumpscaleLib.sal.kvm.Pool import Pool
from JumpscaleLib.sal.kvm.StorageController import StorageController
from JumpscaleLib.sal.kvm.KVMController import KVMController
from JumpscaleLib.sal.kvm.Machine import Machine
from JumpscaleLib.sal.kvm.CloudMachine import CloudMachine
from JumpscaleLib.sal.kvm.MachineSnapshot import MachineSnapshot

JSBASE = j.application.JSBaseClass
class KVM(JSBASE):

    def __init__(self):

        self.__jslocation__ = "j.sal.kvm"
        JSBASE.__init__(self)
        self.__imports__ = "libvirt-python"
        self.KVMController = KVMController
        self.Machine = Machine
        self.MachineSnapshot = MachineSnapshot
        self.Network = Network
        self.Interface = Interface
        self.Disk = Disk
        self.Pool = Pool
        self.StorageController = StorageController
        self.CloudMachine = CloudMachine
