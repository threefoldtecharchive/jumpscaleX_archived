from Jumpscale import j
import textwrap


class BuilderDigitalME(j.builder.system._BaseClass):
    NAME = "digitalme"

    def _init(self):
        pass


    def build(self,reset=False):
        """
        kosmos 'j.tools.sandboxer.sandbox_build()'

        will build python & openresty & copy all to the right git sandboxes works for Ubuntu & OSX
        :return:
        """
        j.builder.runtimes.python.build(reset=reset)
        j.builder.runtimes.python._copy2sandbox_github()
        j.builder.runtimes.lua.build()  # will build openresty & lua & openssl
        j.builder.runtimes.lua.copy2sandbox_github()

        if j.core.platformtype.myplatform.isUbuntu: #only for building
            #no need to sandbox in non linux systems
            j.tools.sandboxer.libs_sandbox("{{DIR_BASE}}/bin", "{{DIR_BASE}}/lib", True)
            # TODO: Check if still needed
            # j.tools.sandboxer.libs_sandbox("{{BASE_DIR}}/lib", "{{BASE_DIR}}/lib"% self.PACKAGEDIR, True)
        else:
            # FIXME : support OSX
            j.shell()

    def sandbox(self,destination_dir="/tmp/builder/{NAME}", flist=True, zhub_instance=None):
        destination_dir = self.tools.replace(destination_dir,args={"NAME":self.__class__.NAME})
        raise RuntimeError("needs to be implemented")


    def test(self,zos_client):
        """

        :return:
        """

        self.build()
        flist = self.sandbox()  #will not upload to zhub_instance


        #create container and use this flist
        #see that openresty is working


