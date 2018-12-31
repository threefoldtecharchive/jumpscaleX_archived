from Jumpscale import j

class BuilderBaseClass(j.application.JSBaseClass):


    @property
    def system(self):
        return j.builder.system

    @property
    def tools(self):
        return j.builder.tools

    @property
    def b(self):
        return j.builder

