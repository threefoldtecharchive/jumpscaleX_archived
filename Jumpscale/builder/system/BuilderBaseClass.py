from Jumpscale import j

class BuilderBaseClass(j.application.JSBaseClass):


    def _init(self):
        self.system = j.builder.system
        self.tools = j.builder.tools
        self.b = j.builder

