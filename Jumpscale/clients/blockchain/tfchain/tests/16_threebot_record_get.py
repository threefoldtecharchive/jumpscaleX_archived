from Jumpscale import j

import pytest

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub
from Jumpscale.clients.blockchain.tfchain.TFChainClient import ThreeBotRecord
from Jumpscale.clients.blockchain.tfchain.types.ThreeBot import BotName, NetworkAddress
from Jumpscale.clients.blockchain.tfchain.types.CryptoTypes import PublicKey


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="threebot_record_get")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mytestclient", network_type="DEV")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    # add threebot record:
    explorer_client.threebot_record_add(
        ThreeBotRecord(
            identifier=3,
            names=[BotName(value="chatbot.example")],
            addresses=[NetworkAddress(address="example.org")],
            public_key=PublicKey.from_json("ed25519:e4f55bc46b5feb37c03a0faa2d624a9ee1d0deb5059aaa9625d8b4f60f29bcab"),
            expiration=1552581420,
        )
    )
    # overwrite the external get logic
    c._explorer_get = explorer_client.explorer_get

    # all the following will allow you to get the same 3Bot record
    for identifier in [
        3,
        BotName(value="chatbot.example"),
        "chatbot.example",
        "ed25519:e4f55bc46b5feb37c03a0faa2d624a9ee1d0deb5059aaa9625d8b4f60f29bcab",
        PublicKey.from_json("ed25519:e4f55bc46b5feb37c03a0faa2d624a9ee1d0deb5059aaa9625d8b4f60f29bcab"),
    ]:
        record = c.threebot.record_get(identifier)
        # the unique 3Bot identifier can be accessed
        assert record.identifier == 3
        # all names (aliases of the 3Bot) can be accessed
        assert len(record.names) == 1
        assert record.names[0].value == "chatbot.example"
        # all network addresses that point can be accessed
        assert len(record.addresses) == 1
        assert record.addresses[0].value == "example.org"
        # public key can be accessed
        assert (
            record.public_key.unlockhash
            == "01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0"
        )
        # timestamp on which the 3Bot expires, unless more months are paid (see Record Update)
        assert record.expiration == 1552581420

    # if the 3Bot cannot be found, the j.clients.tfchain.errors.ThreeBotNotFound exception will be raised
    with pytest.raises(j.clients.tfchain.errors.ThreeBotNotFound):
        c.threebot.record_get(1)
