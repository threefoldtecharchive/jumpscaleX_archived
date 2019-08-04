from Jumpscale import j

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="blockstake_output_get")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mytestclient", network_type="TEST")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    # spent block stake output
    explorer_client.hash_add(
        "fb3644143770aeef28020b8bea7c35320cb1e2341d17a338389bd7e3afb9990b",
        '{"hashtype":"blockstakeoutputid","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"a277de3f98a75e3199b1829b4f71093b23044e0fc995cb98224fe22ebda14c84","height":14733,"parent":"62d947526f5012d771c9618851fbf7069930a9106c53cd89dda858738b84f6f1","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"a877078376f423d4f7a477959adffdaa58e445f39ef00c94330d7bf89a053535","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"b52b1aedb4e228914356490467cfcdae4d09d68c214806b358e8e503232fd9d5865ff14ed9196154343498001a25c17396e2109015f21c67387c9a5ea9490706"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["fb3644143770aeef28020b8bea7c35320cb1e2341d17a338389bd7e3afb9990b"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false},{"id":"ba0be0145a3415440eddf5cf6f5268e3119c4ab67207652efb6783f0723b0aba","height":14734,"parent":"1f9454cef5a71e9b43ef2eae35bfb6171b596e96177d9a6ef59a9bd2ec854b30","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"fb3644143770aeef28020b8bea7c35320cb1e2341d17a338389bd7e3afb9990b","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"7ea47daa3d131f9bb28a7b0aebc9c9399ba6d9f1ae216d85ff6a6735362f9fc4bca4c0ec3de2d5b386187d882f7b5f76e9846e5f6c559d3bb196dd38c6d46e0c"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["cf9dc7e9bf57d2ad9be81fa9d1039f41e55afc743f7bce5e5379cf4d8a8ce018"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false}],"multisigaddresses":null,"unconfirmed":false}',
    )
    c._explorer_get = explorer_client.explorer_get

    # get a blockstake output that has already been spent
    bso, creation_txn, spend_txn = c.blockstake_output_get(
        "fb3644143770aeef28020b8bea7c35320cb1e2341d17a338389bd7e3afb9990b"
    )
    assert spend_txn is not None
    assert bso is not None
    assert creation_txn is not None
    assert bso.id == "fb3644143770aeef28020b8bea7c35320cb1e2341d17a338389bd7e3afb9990b"
    assert str(bso.value) == "3000"
    assert (
        str(bso.condition.unlockhash)
        == "015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"
    )
    assert str(creation_txn.id) == "a277de3f98a75e3199b1829b4f71093b23044e0fc995cb98224fe22ebda14c84"
    assert len(creation_txn.coin_inputs) == 0
    assert len(creation_txn.coin_outputs) == 0
    assert len(creation_txn.blockstake_inputs) == 1
    assert (
        str(creation_txn.blockstake_inputs[0].parentid)
        == "a877078376f423d4f7a477959adffdaa58e445f39ef00c94330d7bf89a053535"
    )
    assert len(creation_txn.blockstake_outputs) == 1
    assert creation_txn.blockstake_outputs[0] == bso
    assert str(spend_txn.id) == "ba0be0145a3415440eddf5cf6f5268e3119c4ab67207652efb6783f0723b0aba"
    assert len(spend_txn.blockstake_inputs) == 1
    assert spend_txn.blockstake_inputs[0].parentid == bso.id
