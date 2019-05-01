from Jumpscale import j


class BuilderBlockchainFactory(j.builder.system._BaseFactoryClass):

    __jslocation__ = "j.builder.blockchain"

    def _init(self):

        from .BuilderTFChain import BuilderTFChain
        self.tfchain = BuilderTFChain()

        from .BuilderEthereum import BuilderEthereum
        self.ethereum = BuilderEthereum()

        from .BuilderBitcoin import BuilderBitcoin
        self.bitcoin = BuilderBitcoin()
