from Jumpscale import j




class BuilderProtobuf(j.builder.system._BaseClass):

    NAME = "protoc"

    def install(self, reset=False):
        """
        install protobut
        """
        if self.doneCheck("install", reset):
            return

        j.builder.system.package.mdupdate()
        if j.builder.core.isMac:
            j.builder.tools.package_install(['protobuf'])
        else:
            url="https://github.com/google/protobuf/releases/download/v3.4.0/protoc-3.4.0-linux-x86_64.zip"
            res=j.builder.network.tools.download(url, to='', overwrite=False, retry=3, timeout=0, expand=True,removeTopDir=False)
            j.builder.core.file_move("%s/bin/protoc"%res,"/usr/local/bin/protoc")
        j.builder.system.python_pip.install(
            "protobuf3", upgrade=True)  # why not protobuf?

        self.doneSet("install")
