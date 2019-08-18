from Jumpscale import j

import pytest

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub
from Jumpscale.clients.blockchain.tfchain.types.AtomicSwap import AtomicSwapContract


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="atomicswap_participate")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mytestclient", network_type="TEST")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    # add the blockchain info
    explorer_client.chain_info = '{"blockid":"583266f598044ebd971110bd03510e950361c22b4ed818e7644b6d59c36fd5bc","difficulty":"29305","estimatedactivebs":"2067","height":16922,"maturitytimestamp":1549649615,"target":[0,2,60,124,18,9,53,143,255,130,219,75,17,252,30,24,177,101,116,228,26,221,54,224,30,251,45,78,1,199,78,60],"totalcoins":"0","arbitrarydatatotalsize":4351,"minerpayoutcount":17006,"transactioncount":17547,"coininputcount":635,"coinoutputcount":1228,"blockstakeinputcount":16922,"blockstakeoutputcount":16923,"minerfeecount":624,"arbitrarydatacount":573}'
    explorer_client.hash_add(
        "583266f598044ebd971110bd03510e950361c22b4ed818e7644b6d59c36fd5bc",
        '{"hashtype":"blockid","block":{"minerpayoutids":["eb538b38d8fcf7b0ef037eccf8cab1096c2b98031311453c150b2b150c483941"],"transactions":[{"id":"92132a65558684f154a56232acf9b7dd1e003d0f3ebdb2c4b44494d3c5e7f658","height":16922,"parent":"583266f598044ebd971110bd03510e950361c22b4ed818e7644b6d59c36fd5bc","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"ca1da3d88904a532692ad2bb67122747eea4d91ead119043253ecb34410bbcc3","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"120c7bdf823a45fde303a725a1d757b3ece975abcd326ec036c056c6499b6de6cd798f18f8dff8c7adebcf19901e358609e675871335a71678c17de3e1dadb04"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["615f6f9d28d97082b423de7a878830b739b8fc4737c7ed20d3923a0019dbaed6"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false}],"rawblock":{"parentid":"35879735f395c25fa7c0366bec7002f960798517e5335b5f27348c3a1b1923d4","timestamp":1549649728,"pobsindexes":{"BlockHeight":16921,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"transactions":[{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"ca1da3d88904a532692ad2bb67122747eea4d91ead119043253ecb34410bbcc3","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"120c7bdf823a45fde303a725a1d757b3ece975abcd326ec036c056c6499b6de6cd798f18f8dff8c7adebcf19901e358609e675871335a71678c17de3e1dadb04"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}}]},"blockid":"583266f598044ebd971110bd03510e950361c22b4ed818e7644b6d59c36fd5bc","difficulty":"29305","estimatedactivebs":"2067","height":16922,"maturitytimestamp":1549649615,"target":[0,2,60,124,18,9,53,143,255,130,219,75,17,252,30,24,177,101,116,228,26,221,54,224,30,251,45,78,1,199,78,60],"totalcoins":"0","arbitrarydatatotalsize":4351,"minerpayoutcount":17006,"transactioncount":17547,"coininputcount":635,"coinoutputcount":1228,"blockstakeinputcount":16922,"blockstakeoutputcount":16923,"minerfeecount":624,"arbitrarydatacount":573},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}',
    )
    # add the wallet info
    explorer_client.hash_add(
        "01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0",
        '{"hashtype":"unlockhash","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"bca044302e018e67600bd0bd3223ae8dbb702eb528e73d6cfa9d057d4f73b03a","height":16911,"parent":"b4882a0b8632396a9c5d83a5c8684ab76736f4bff6d971795ed7334fac8aa339","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"357451c3f3a15f6150aedede9d5228ec5dfc2d32c9b62c2a46128533a7845c72","fulfillment":{"type":1,"data":{"publickey":"ed25519:fdb2e1b898dda304f748c0ff812a24729b2aafd344512079ab778eb368b18645","signature":"bd9dd36e86c08a5990ad5282d1079705c3a4b1cf3896e96791aa7db97002d5eb002c50467f45bd3ac1086292932cd2ab53c91b2e8bb74b9d9c9c0d558082ef08"}}}],"coinoutputs":[{"value":"51000000000","condition":{"type":1,"data":{"unlockhash":"01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0"}}},{"value":"99994187000000000","condition":{"type":1,"data":{"unlockhash":"0183841ae8952a2ba72db0d6fce6208df70f2a936ee589ff852e06b20af48b40489572b1a69b2a"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"99994239000000000","condition":{"type":1,"data":{"unlockhash":"019bb005b78a47fd084f4f3a088d83da4fadfc8e494ce4dae0d6f70a048a0a745d88ace6ce6f1c"}},"unlockhash":"019bb005b78a47fd084f4f3a088d83da4fadfc8e494ce4dae0d6f70a048a0a745d88ace6ce6f1c"}],"coinoutputids":["753aaeaa0c9e6c9f1f8da1974c83d8ca067ad536f464a2e2fc038bbd0404d084","8c8dbd70c6eb2d5d181aa5ae430f2cc86e038b92e45dd6f6d5a28400efad4511"],"coinoutputunlockhashes":["01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0","0183841ae8952a2ba72db0d6fce6208df70f2a936ee589ff852e06b20af48b40489572b1a69b2a"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"multisigaddresses":null,"unconfirmed":false}',
    )
    # override internal functionality, as to use our stub client
    c._explorer_get = explorer_client.explorer_get
    c._explorer_post = explorer_client.explorer_post

    # a wallet is required to initiate an atomic swap contract
    w = c.wallets.new(
        "mytestwallet",
        seed="remain solar kangaroo welcome clean object friend later bounce strong ship lift hamster afraid you super dolphin warm emotion curve smooth kiss stem diet",
    )
    # money is required to be available in the wallet
    assert str(w.balance.available) == "51"

    # a participation atomic swap contract can be created and signed as follows:
    result = w.atomicswap.participate(
        initiator="01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c",
        amount=50,
        secret_hash="4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba",
        submit=False,
    )  # submit=True is the default
    assert not result.submitted
    assert result.transaction.is_fulfilled()
    # the contract is returned as part of the result
    assert str(result.contract.amount) == "50"
    assert (
        str(result.contract.sender) == "01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0"
    )
    assert (
        str(result.contract.receiver)
        == "01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c"
    )
    assert result.contract.refund_timestamp > 1549649728
    assert result.contract.secret_hash == "4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba"
    # one would than use `w.transaction_sign(result.transaction)` to submit it for real

    # however, usually an atomic swap contract is participated as follows:
    result = w.atomicswap.participate(
        initiator="01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c",
        amount=50,
        secret_hash="4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba",
    )
    assert result.submitted
    # the contract is returned as part of the result
    assert str(result.contract.amount) == "50"
    assert (
        str(result.contract.sender) == "01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0"
    )
    assert (
        str(result.contract.receiver)
        == "01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c"
    )
    assert result.contract.refund_timestamp > 1549649728
    assert result.contract.secret_hash == "4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba"

    # ensure our contract was submitted
    transaction = explorer_client.posted_transaction_get(result.transaction.id)
    contract = AtomicSwapContract(transaction.coin_outputs[0], unspent=True)
    assert contract == result.contract
    # and ensure the transaction is fully signed
    for ci in transaction.coin_inputs:
        assert len(ci.fulfillment.signature.value) == 64

    # FYI: a contract's amount has to be greater than the network's minimum miner fee,
    # while tfchain does allow it, this client will raise an exception when you
    # do try to give a value equal to or less than the networks' miner fee.
    # This because such a contract cannot be redeemed or refunded.
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapInsufficientAmountError):
        w.atomicswap.participate(
            initiator="01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c",
            amount=c.minimum_miner_fee - "0.000000001 TFT",
            secret_hash="4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba",
        )
