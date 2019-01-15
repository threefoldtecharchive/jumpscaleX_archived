from .TfChain import TfChainClient, TfChainExplorer
from Jumpscale import j

JSBASE = j.application.JSBaseClass


class TfChainFactory(JSBASE):
    __jslocation__ = "j.sal_zos.tfchain"

    def explorer(self, name, container, domain, data_dir='/mnt/data', rpc_addr='0.0.0.0:23112', api_addr='localhost:23110', network='standard'):
        return TfChainExplorer(name=name, container=container, data_dir=data_dir, rpc_addr=rpc_addr, api_addr=api_addr, domain=domain, network=network)

    def client(self, name, container, wallet_passphrase, api_addr='localhost:23110'):
        return TfChainClient(name=name, container=container, addr=api_addr, wallet_passphrase=wallet_passphrase)
