"""
Tfchain Client
"""

from Jumpscale import j
from json import dumps

from clients.blockchain.tfchain.errors import InvalidTfchainNetwork, NoExplorerNetworkAddresses
from clients.blockchain.tfchain.TfchainNetwork import TfchainNetwork
from clients.blockchain.rivine.RivineWallet import RivineWallet

TEMPLATE = """
network = "{}"
seed_ = ""
explorers = {}
password = ""
nr_keys_per_seed = 1
""".format(
    TfchainNetwork.STANDARD.name.lower(),
    dumps(TfchainNetwork.STANDARD.official_explorers()))

JSConfigBase = j.application.JSBaseClass

class TfchainClient(JSConfigBase):
    """
    Tfchain client object
    """
    def __init__(self, instance, data=None, parent=None, interactive=False):
        """
        Initializes a new Tfchain Client
        """
        if not data:
            data = {}

        JSConfigBase.__init__(self, instance, data=data, parent=parent,
                template=TEMPLATE, interactive=interactive)
        self._wallet = None

    @property
    def wallet(self):
        if self._wallet is None:
            client = j.clients.tfchain.get(self.instance, create=False)
            # Load the correct config params specific to the network
            network = TfchainNetwork(self.config.data['network'])
            if not isinstance(network, TfchainNetwork):
                raise InvalidTfchainNetwork("invalid tfchain network specified")
            minerfee = network.minimum_minerfee()
            explorers = self.config.data['explorers']
            if not explorers :
                explorers = network.official_explorers()
                if not explorers:
                    raise NoExplorerNetworkAddresses("network {} has no official explorer networks and none were specified by callee".format(network.name.lower()))
            # Load a wallet from a given seed. If no seed is given,
            # generate a new one
            seed = self.config.data['seed_']
            if seed == "":
                seed = self.generate_seed()
                # Save the seed in the config
                data = dict(self.config.data)
                data['seed_'] = seed
                cl = j.clients.tfchain.get(instance=self.instance,
                        data=data,
                        create=True,
                        interactive=False)
                cl.config.save()
                # make sure to set the seed in the current object.
                # if not, we'd have a random non persistent seed until
                # the first reload
                self.config.data['seed_'] = seed
            self._wallet = RivineWallet(seed=seed,
                    bc_networks = explorers,
                    bc_network_password = self.config.data['password'],
                    nr_keys_per_seed = self.config.data['nr_keys_per_seed'],
                    minerfee = minerfee,
                    client=client)
        return self._wallet

    def generate_seed(self):
        """
        Generate a new seed
        """
        return j.data.encryption.mnemonic.generate(strength=256)
