"""
Jumpscale client module that define a client for electrum wallet
"""

from Jumpscale import j

from JumpscaleLib.clients.blockchain.electrum.ElectrumWallet import ElectrumWallet
from JumpscaleLib.clients.blockchain.electrum.ElectrumAtomicswap import ElectrumAtomicswap


TEMPLATE = """
server = "localhost:7777:s"
rpc_user = "user"
rpc_pass_ = "pass"
seed_ = ""
fee = 10000
password_ = ""
passphrase_ = ""
electrum_path = ""
testnet = 0
"""



JSConfigBase = j.application.JSBaseClass


class ElectrumClient(JSConfigBase):
    """
    Electrum client object
    """
    def __init__(self, instance, data=None, parent=None, interactive=False):
        """
        Initializes new Rivine Client
        """
        if not data:
            data = {}

        JSConfigBase.__init__(self, instance=instance, data=data, parent=parent,
                              template=TEMPLATE, interactive=interactive)
        self._wallet = None
        self._atomicswap = None


    @property
    def wallet(self):
        # access atomicswap to make sure the wallet is loaded
        # need to figure out a better wayt to do this using a call to the library
        self.atomicswap
        if self._wallet is None:
            config_data = {}
            for key, value in self.config.data.items():
                config_data[key.strip('_')] = value
            self._wallet = ElectrumWallet(name=self.instance, config=config_data)
        return self._wallet


    @property
    def atomicswap(self):
        """
        Atomicswap support for BTC electrum
        """
        if self._atomicswap is None:
            self._atomicswap = ElectrumAtomicswap(wallet_name=self.instance,
                                                  data_dir=self.config.data['electrum_path'],
                                                  rpcuser=self.config.data['rpc_user'],
                                                  rpcpass=self.config.data['rpc_pass_'],
                                                  rpchost=self.config.data['server'].split(':')[0],
                                                  rpcport=self.config.data['server'].split(':')[1],
                                                  testnet=self.config.data['testnet'])
        return self._atomicswap
