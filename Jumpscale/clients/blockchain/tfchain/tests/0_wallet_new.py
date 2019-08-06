from Jumpscale import j

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="wallet_new")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mydevclient", network_type="DEV")
    # or simply `c = j.tfchain.clients.mydevclient`, should the client already exist

    # for standard net you could also immediate create a new wallet using
    # `c = j.tfchain.clients.mydevclient`, or the more explicit form
    # `c = j.clients.tfchain.get("mydevclient", network_type="STD")`

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    c._explorer_get = explorer_client.explorer_get

    # create a new devnet wallet
    w = c.wallets.get("mywallet")  # is the implicit form of `c.wallets.new("mywallet")`

    # a tfchain (JS) wallet uses the underlying tfchain client for all its
    # interaction with the tfchain network
    assert w.network_type == "DEV"

    # the seed is the mnemonic used to generate the entropy from
    assert len(w.seed) > 0
    # the entropy is used to generate the private keys of this wallet,
    # only one private key by default, and for each private key a public key is generated as well
    assert len(w.seed_entropy) > 0

    # a wallet address is generated from the blake2 hash of a public key, owned by the wallet
    assert len(w.addresses) == 1
    # should you want to know the address count there is a property for that
    assert w.key_count == 1

    # generating a new address is easy as well
    assert len(w.address_new()) == 78  # all addresses have a fixed length of 78
    assert w.key_count == 2
    assert w.addresses[0] != w.addresses[1]
    for address in w.addresses:
        assert address[:2] == "01"  # all wallet addresses start with the `01` prefix

    # the private public key pair, for a given unlock hash, is available as well,
    # but is meant for dev purposes, not for an end-user
    for address in w.addresses:
        assert address == str(w.key_pair_get(address).unlockhash)
