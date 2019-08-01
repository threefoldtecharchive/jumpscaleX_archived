from Jumpscale import j

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="minter_condition_get")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mytestclient", network_type="TEST")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    # add initial mint condition
    explorer_client.mint_condition_add(
        condition=j.clients.tfchain.types.conditions.from_recipient(
            "01a006599af1155f43d687635e9680650003a6c506934996b90ae84d07648927414046f9f0e936"
        ),
        height=0,
    )
    # overwrite explorer get logic
    c._explorer_get = explorer_client.explorer_get

    # getting the latest mint condition is as easy as making the following call:
    condition = c.minter.condition_get()
    assert condition.unlockhash == "01a006599af1155f43d687635e9680650003a6c506934996b90ae84d07648927414046f9f0e936"

    # you can also get the condition active for a certain block height as follows:
    for height in [0, 500, 23400, 120000]:
        # as there is only one mint condition registered at the moment, it will return that one no matter what
        condition = c.minter.condition_get(height)
        assert condition.unlockhash == "01a006599af1155f43d687635e9680650003a6c506934996b90ae84d07648927414046f9f0e936"

    # if another one gets registered,
    explorer_client.mint_condition_add(
        condition=j.clients.tfchain.types.conditions.from_recipient(
            (
                1,
                [
                    "01a006599af1155f43d687635e9680650003a6c506934996b90ae84d07648927414046f9f0e936",
                    "011cf61451b58970eeead00819e33f7fc812bd9b2d4e66914efa6163e238752d34be252ac8667f",
                ],
            )
        ),
        height=50,
    )
    # it will return the latest condition when requesting the latest,
    # and it will return the one active at the current height
    condition = c.minter.condition_get()
    assert condition.unlockhash == "037187176be3a123b545209d933f4250a20f4baac78051c0993653500e9d6bc46d290e499b058c"
    for height in [0, 1, 23, 49]:
        condition = c.minter.condition_get(height)
        assert condition.unlockhash == "01a006599af1155f43d687635e9680650003a6c506934996b90ae84d07648927414046f9f0e936"
    for height in [50, 51, 200, 500, 15000]:
        condition = c.minter.condition_get(height)
        assert condition.unlockhash == "037187176be3a123b545209d933f4250a20f4baac78051c0993653500e9d6bc46d290e499b058c"
