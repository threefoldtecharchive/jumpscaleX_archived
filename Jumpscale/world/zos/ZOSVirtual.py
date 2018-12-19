from Jumpscale import j


class ZOSVirtual(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    @url = jumpscale.clients.zoscmd.zosvirtual.1
    name = "" (S)
    ssh_addr = "127.0.0.1" (S)
    ssh_port = 22 (S)
    zos_addr = "127.0.0.1" (S)
    zos_port = 6379 (I)
    secret = "" (S)    
    """

    def _init(self):
        self.ZOSNode = None  #links to the ZOSNode which hosts this ZOSContainer

    @property
    def zos_client(self):
        """
        return zos protocol client
        :return:
        """
        pass
        #implement caching at client side

    def ssh_client(self):
        """

        :return: ssh client to this container
        """
        pass
        #implement caching at client side


    def __str__(self):
        return "zoscontainer:%-14s %-25s:%-4s" % (self.name, self.addr,self.port)

    __repr__ = __str__


#REMARK: create an SSH connection to the ZOS node, can only be done when virtual


#IMPLEMENT START/....

