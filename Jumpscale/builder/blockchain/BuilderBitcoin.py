from Jumpscale import j



class BuilderBitcoin(j.builder.system._BaseClass):
    NAME = "bitcoind"

    def _init(self):
        self.BITCOIN_64BIT_URL = "https://bitcoin.org/bin/bitcoin-core-0.16.0/bitcoin-0.16.0-x86_64-linux-gnu.tar.gz"
        self.DOWNLOAD_DEST = j.core.tools.text_replace("{DIR_VAR}/build/bitcoin-0.16.0.tar.gz")
        self.EXTRACTED_FILEPATH = j.core.tools.text_replace("{DIR_TEMP}/bitcoin-0.16.0")


    def build(self, reset=False):
        """Get/Build the binaries of bitcoin
        Keyword Arguments:
            reset {bool} -- reset the build process (default: {False})
        """

        if self._done_get('build') and reset is False:
            return

        if not j.builder.tools.file_exists(self.DOWNLOAD_DEST):
            j.builder.tools.file_download(self.BITCOIN_64BIT_URL, self.DOWNLOAD_DEST)

        j.builder.tools.file_expand(self.DOWNLOAD_DEST, "{DIR_TEMP}")

        self._done_set('build')


    def install(self, reset=False):
        """
        Install the bitcoind binaries
        """

        if self._done_get('install') and reset is False:
            return

        self.build(reset=reset)

        cmd = j.core.tools.text_replace('cp {}/bin/* {DIR_BIN}/'.format(self.EXTRACTED_FILEPATH))
        j.sal.process.execute(cmd)

        cmd = j.core.tools.text_replace('cp {}/lib/* $LIBDIR/'.format(self.EXTRACTED_FILEPATH))
        j.sal.process.execute(cmd)

        self._done_set('install')
