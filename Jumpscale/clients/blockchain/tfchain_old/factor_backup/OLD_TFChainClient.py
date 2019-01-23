"""
Tfchain Client
"""

from Jumpscale import j

from clients.blockchain.tfchain.errors import InvalidTfchainNetwork, NoExplorerNetworkAddresses

from clients.blockchain.rivine.RivineWallet import RivineWallet


EXPLORER_NODES_STD = [
                'https://explorer.threefoldtoken.com',
                'https://explorer2.threefoldtoken.com',
                'https://explorer3.threefoldtoken.com',
                'https://explorer4.threefoldtoken.com',
            ]

EXPLORER_NODES_TEST = [
                'https://explorer.testnet.threefoldtoken.com',
                'https://explorer2.testnet.threefoldtoken.com',
            ]

EXPLORER_NODES_DEV = [
                'http://localhost:23112'
            ]


class TFChainBaseClient(j.application.JSBaseConfigClass):
    """
    Tfchain client object
    """
    _SCHEMATEXT = """
        @url = jumpscale.tfchain.client
        name* = "" (S)
        network = "" (LS)
        seed = "" (S)
        network_type = "STD,TEST,DEV" (E)
        password = "" (S)
        nr_keys_per_seed = 1 (I)       
        minimum_minerfee = 100000000 (I)
        explorer_nodes = (LO) !jumpscale.tfchain.explorer
        
        @url = jumpscale.tfchain.explorer
        addr = "" (S)
        port = 443 (I)
        """


    def _data_trigger_new(self):
        if self.network_type in ["DEV"]:
            self.minimum_minerfee = 1000000000


    @property
    def explorer_addresses(self):
        j.shell()


    @property
    def wallet(self):
        if self._wallet is None:
            client = j.clients.tfchain.get(self.instance, create=False)
            # Load the correct config params specific to the network
            network = TfchainNetwork(self.network)
            if not isinstance(network, TfchainNetwork):
                raise InvalidTfchainNetwork(
                    "invalid tfchain network specified")
            minerfee = network.minimum_minerfee()
            explorers = self.explorers
            if not explorers:
                explorers = network.official_explorers()
                if not explorers:
                    raise NoExplorerNetworkAddresses(
                        "network {} has no official explorer networks and none were specified by callee".format(network.name.lower()))
            # Load a wallet from a given seed. If no seed is given,
            # generate a new one
            seed = self.seed_
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
                self.seed_ = seed
            self._wallet = RivineWallet(seed=seed,
                                        bc_networks=explorers,
                                        bc_network_password=self.password,
                                        nr_keys_per_seed=self.nr_keys_per_seed,
                                        minerfee=minerfee,
                                        client=client)
        return self._wallet

    def generate_seed(self):
        """
        Generate a new seed
        """
        return j.data.encryption.mnemonic.generate(strength=256)
