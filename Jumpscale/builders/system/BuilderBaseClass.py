from Jumpscale import j

class JSBase(j.application.JSBaseClass):


    def _init(self):
        self.core = j.builder.core
        self.system = j.builder.system
        self.tools = j.builder.tools
        self.b = j.builder
