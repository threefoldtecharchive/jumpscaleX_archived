from Jumpscale import j

import pytest

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub
from Jumpscale.clients.blockchain.tfchain.types.FulfillmentTypes import (
    FulfillmentSingleSignature,
    FulfillmentMultiSignature,
)


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="minter_condition_set")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mydevclient", network_type="DEV")
    # or simply `c = j.tfchain.clients.mydevclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    # define current block height
    explorer_client.chain_info = '{"blockid":"552e410481cce1358ffcd4687f4199dd2181c799d55da26178e55643355bbd2e","difficulty":"27801","estimatedactivebs":"59","height":3644,"maturitytimestamp":1549012510,"target":[0,2,91,116,78,165,130,72,116,162,127,4,125,67,108,16,140,247,132,198,107,159,114,177,44,25,18,162,38,157,169,245],"totalcoins":"0","arbitrarydatatotalsize":6,"minerpayoutcount":3650,"transactioncount":3652,"coininputcount":12,"coinoutputcount":15,"blockstakeinputcount":3644,"blockstakeoutputcount":3645,"minerfeecount":7,"arbitrarydatacount":1}'
    explorer_client.hash_add(
        "552e410481cce1358ffcd4687f4199dd2181c799d55da26178e55643355bbd2e",
        '{"hashtype":"blockid","block":{"minerpayoutids":["468db689f752414702ef3a5aa06238f03a4539434a61624b3b8a0fb5dc38a211"],"transactions":[{"id":"2396f8e57bbb9b22bd1d749d5de3fd532ea6886e9660a556a13571d701d83e27","height":3644,"parent":"552e410481cce1358ffcd4687f4199dd2181c799d55da26178e55643355bbd2e","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"ff5a002ec356b7cb24fbee9f076f239fb8c72d5a8a448cee92ee6d29a87aef52","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"7bec94dfb87640726c6a14de2110599db0f81cf9fa456249e7bf79b0c74b79517edde25c4ee87f181880af44fe6ee054ff20b74eda2144fe07fa5bfb9d884208"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["f683e7319659c61f54e93546bc41b57c5bffe79de26c06ec7371034465804c81"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false}],"rawblock":{"parentid":"47db4274551b0372564f8d1ab89c596428f00e460c0b416327e53983c8765198","timestamp":1549012665,"pobsindexes":{"BlockHeight":3643,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"transactions":[{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"ff5a002ec356b7cb24fbee9f076f239fb8c72d5a8a448cee92ee6d29a87aef52","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"7bec94dfb87640726c6a14de2110599db0f81cf9fa456249e7bf79b0c74b79517edde25c4ee87f181880af44fe6ee054ff20b74eda2144fe07fa5bfb9d884208"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}}]},"blockid":"552e410481cce1358ffcd4687f4199dd2181c799d55da26178e55643355bbd2e","difficulty":"27801","estimatedactivebs":"59","height":3644,"maturitytimestamp":1549012510,"target":[0,2,91,116,78,165,130,72,116,162,127,4,125,67,108,16,140,247,132,198,107,159,114,177,44,25,18,162,38,157,169,245],"totalcoins":"0","arbitrarydatatotalsize":6,"minerpayoutcount":3650,"transactioncount":3652,"coininputcount":12,"coinoutputcount":15,"blockstakeinputcount":3644,"blockstakeoutputcount":3645,"minerfeecount":7,"arbitrarydatacount":1},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}',
    )
    # add initial condition
    explorer_client.mint_condition_add(
        condition=j.clients.tfchain.types.conditions.from_recipient(
            "01a006599af1155f43d687635e9680650003a6c506934996b90ae84d07648927414046f9f0e936"
        ),
        height=0,
    )
    # overwrite get/post logic
    c._explorer_get = explorer_client.explorer_get
    c._explorer_post = explorer_client.explorer_post

    # the devnet genesis seed is the seed of the wallet,
    # which receives all block stakes and coins in the genesis block of the tfchain devnet
    DEVNET_GENESIS_SEED = "image orchard airport business cost work mountain obscure flee alpha alert salmon damage engage trumpet route marble subway immune short tide young cycle attract"

    # create a new devnet wallet
    w = c.wallets.new("mywallet", seed=DEVNET_GENESIS_SEED)
    # we create a new wallet using an existing seed,
    # such that our seed is used and not a new randomly generated seed

    # only if you have the correct minting powers,
    # you can set a new minter definition, otherwise an error will be raised

    # set another mint condition manually
    explorer_client.mint_condition_add(
        condition=j.clients.tfchain.types.conditions.from_recipient(
            "014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"
        ),
        height=3643,
    )

    condition = c.minter.condition_get()
    assert condition.unlockhash == w.address

    # (1) once you have the correct powers, you can can overwrite it as follows:
    result = w.minter.definition_set(
        minter=(
            1,
            [
                "014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a",
                "011cf61451b58970eeead00819e33f7fc812bd9b2d4e66914efa6163e238752d34be252ac8667f",
            ],
        )
    )
    # check if the current transaction is submitted
    assert result.submitted  # it is expected

    # check if all is fulfilled
    assert result.transaction.is_fulfilled()
    assert result.transaction.mint_fulfillment.is_fulfilled(parent_condition=c.minter.condition_get())
    assert isinstance(result.transaction.mint_fulfillment, FulfillmentSingleSignature)
    # ensure the transaction is posted and as expected there as well
    txn = explorer_client.posted_transaction_get(result.transaction.id)
    assert txn.json() == result.transaction.json()

    # set another mint condition manually
    explorer_client.mint_condition_add(
        condition=j.clients.tfchain.types.conditions.from_recipient(
            (
                1,
                [
                    "014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a",
                    "011cf61451b58970eeead00819e33f7fc812bd9b2d4e66914efa6163e238752d34be252ac8667f",
                ],
            )
        ),
        height=3644,
    )

    # (2) when defining a new minter definition you can also attach data if desired
    result = w.minter.definition_set(
        minter="011cf61451b58970eeead00819e33f7fc812bd9b2d4e66914efa6163e238752d34be252ac8667f",  # new minter power
        data="redefine minter conditions",  # optional data, can also be as binary data
    )
    assert result.submitted  # it is expected the transaction is submitted
    assert result.transaction.is_fulfilled()
    assert result.transaction.mint_fulfillment.is_fulfilled(parent_condition=c.minter.condition_get())
    assert isinstance(result.transaction.mint_fulfillment, FulfillmentMultiSignature)
    # ensure the transaction is posted and as expected there as well
    txn = explorer_client.posted_transaction_get(result.transaction.id)
    assert txn.json() == result.transaction.json()

    # set another mint condition manually
    explorer_client.mint_condition_add(
        condition=j.clients.tfchain.types.conditions.from_recipient(
            "011cf61451b58970eeead00819e33f7fc812bd9b2d4e66914efa6163e238752d34be252ac8667f"
        ),
        height=3645,
    )

    # if an invalid recipient is given it, a ValueError or TypeError is raised
    with pytest.raises(ValueError):
        w.minter.definition_set(minter=None)
    with pytest.raises(ValueError):
        w.minter.definition_set(minter="0123bla")
    with pytest.raises(TypeError):
        w.minter.definition_set(minter=1)

    # (3) if the wallet has no powers to redefine the powers,
    # the transaction will be not be submitted as the transaction won't be fulfilled
    result = w.minter.definition_set(
        minter="014ad318772a09de75fb62f084a33188a7f6fb5e7b68c0ed85a5f90fe11246386b7e6fe97a5a6a"
    )
    assert not result.submitted
    assert not result.transaction.is_fulfilled()
    assert not result.transaction.mint_fulfillment.is_fulfilled(parent_condition=c.minter.condition_get())
    assert isinstance(result.transaction.mint_fulfillment, FulfillmentSingleSignature)
