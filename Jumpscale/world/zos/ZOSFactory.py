from Jumpscale import j

from .ZOSNode import ZOSNode


JSConfigBase = j.application.JSFactoryBaseClass


class ZOSCmdFactory():

    __jslocation__ = "j.world.zos"

    ZOSNode = ZOSNode

    def _init(self):
        self.zosnodes={}

    def get(self,name,**args):
        if name not in self.zosnodes:
            self.zosnodes[name]=ZOSNode(name=name)
            self.zosnodes[name].data_update(**args)
        return self.zosnodes[name]


    def test(self):
        """

        :return:
        """
        pass

        #TODO: deploy zos in virtualbox
        #...
