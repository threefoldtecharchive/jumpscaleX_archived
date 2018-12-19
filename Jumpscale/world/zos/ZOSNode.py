from Jumpscale import j

from .ZOSContainer import ZOSContainer
from .ZOSVirtual import ZOSVirtual

class ZOSNode(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    @url = jumpscale.clients.zoscmd.zosnode.1
    name = ""
    zos_addr = "127.0.0.1" (S)
    zos_port = 6379 (I)
    local_addr = "127.0.0.1" (S)  #when a private network is available, e.g. in local VirtualBox, can be used to create e.g. ssh connections locally
    secret = "" (S)
    type = "physical" (S) #physical, ovh, ovc, packetnet or virtualbox    
    description = ""
    """

    def _init(self):
        self.ZOSNode = None  #links to the ZOSNode which hosts this ZOSContainer
        self.zos_containers = {}

    @property
    def zos_client(self):
        """
        return zos protocol client
        :return:
        """
        pass
        #implement caching at client side

    def zos_container_get(self,name="test"):
        if name not in self.zos_containers:
            zc = ZOSContainer(name=name)
            zc.zos_node = self
            self.zos_containers[name] = zc
        return self.zos_containers[name]

    def zos_virtual_get(self,name="test"):
        """
        returns a VM which has a ZOS virtual machine
        only works when zosnode is "physical","ovh" or "packetnet"
        :param name:
        :return:
        """
        if self.type not in ["physical","ovh","packetnet"]:
            raise RuntimeError("platform '%s' not supported"%self.type)
        if name not in self.zos_virtual:
            zc = ZOSVirtual(name=name)
            zc.zos_node = self
            self.zos_virtual[name] = zc
        return self.zos_virtual[name]



    def __str__(self):
        return "zosnode:%-14s %-25s:%-4s" % (self.name, self.addr,self.port)

    __repr__ = __str__
