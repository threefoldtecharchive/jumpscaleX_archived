from Jumpscale import j




class BuilderEthereum(j.builder.system._BaseClass):
    NAME = "geth"

    def build(self, reset=False):
        """Build the binaries of ethereum
        Keyword Arguments:
            reset {bool} -- reset the build process (default: {False})
        """

        if self.doneGet('build') and reset is False:
            return

        j.builder.system.installbase.install(upgrade=True)
        j.builder.runtimes.golang.install()
        self.doneSet('build')

    def install(self, reset=False):
        """
        Install the binaries of ethereum
        """
        if self.doneGet('install') and reset is False:
            return

        self.build(reset=reset)
        j.builder.tools.package_install("build-essential")

        geth_path = "{}/src/github.com/ethereum/go-ethereum".format(j.builder.runtimes.golang.GOPATHDIR)

        cmd = """
        go get github.com/ethereum/go-ethereum
        cd {geth_path}
        make geth
        cp build/bin/geth {DIR_BIN}
        """.format(geth_path=geth_path)
        j.sal.process.execute(cmd)

        self.doneSet('install')
