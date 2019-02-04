
from Jumpscale import j




class BuilderNIM(j.builder.system._BaseClass):
    """
    """

    def _init(self):

        self.BUILDDIRL = j.core.tools.text_replace("{DIR_VAR}/build/nimlang/")
        self.CODEDIRL = j.core.tools.text_replace("{DIR_VAR}/build/code/nimlang/")

    def build(self,reset=False):
        """
        js_shell 'j.builder.runtimes.nim.build(reset=False)'
        :return:
        """

        if reset:
            self.reset()

        if self._done_check("build", reset):
            return

        url = "https://nim-lang.org/download/nim-0.19.0.tar.xz"


        j.builder.tools.file_download(url, to=self.CODEDIRL, overwrite=False,
                                       expand=True, minsizekb=400, removeTopDir=True, deletedest=True)

        C="""
        cd {CODEDIRL}
        export LDFLAGS="-L/usr/local/opt/openssl/lib"
        export CPPFLAGS="-I/usr/local/opt/openssl/include"
        export DYLD_LIBRARY_PATH=/usr/local/opt/openssl/lib
        sh build.sh
        sh install.sh ~/.nimble/
        bin/nim c koch
        ./koch tools
        """

        j.builder.tools.run(j.core.tools.text_replace(C))

