from Jumpscale import j

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="transaction_get")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mytestclient", network_type="TEST")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    explorer_client.hash_add(
        "96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec",
        '{"hashtype":"transactionid","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec","height":2662,"parent":"b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f","rawtransaction":{"version":0,"data":{"coininputs":[{"parentid":"c1df239aba64ca0c6a241ddf18f3dd18b75e2c650874dd4c8c7dbbb56bd73683","unlocker":{"type":1,"condition":{"publickey":"ed25519:25b6aae78d545d64746f4a7310230e7b7bce263dcaa9dd5b3b6dd614d0f46413"},"fulfillment":{"signature":"7453f27cca1381f0cc05a6142b8d4ded5c1f84132742ba359df99ea7c17b2f304f8b9c8f3722da9ceb632fb7f526c8022c71e385bb75df9542cf94a7f3f3cc06"}}}],"coinoutputs":[{"value":"1000000000000000","unlockhash":"0199f4f21fc13ceb22da91d4b1701e67556a7c23f118bc5b1b15b132433d07b2496e093c4f4cd6"},{"value":"88839999200000000","unlockhash":"0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2"}],"minerfees":["100000000"]}},"coininputoutputs":[{"value":"89839999300000000","condition":{"type":1,"data":{"unlockhash":"01d1c4dd242e3badf45004be9a3b86c613923c6d872bab5ec92e4f076114d4c3a15b7b43e1c00f"}},"unlockhash":"01d1c4dd242e3badf45004be9a3b86c613923c6d872bab5ec92e4f076114d4c3a15b7b43e1c00f"}],"coinoutputids":["90513506d1216f89e73a361b6306d8543c81aff092e376ee8d8bb9b7ea024de6","7daf8035a6697701aeed36b4d6fe8de6ff4bbf9fd1ba9b0933d87e260f924783"],"coinoutputunlockhashes":["0199f4f21fc13ceb22da91d4b1701e67556a7c23f118bc5b1b15b132433d07b2496e093c4f4cd6","0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}',
    )
    c._explorer_get = explorer_client.explorer_get

    # get a transaction
    txn = c.transaction_get("96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec")

    # from the transaction you can get all kind of info
    assert str(txn.id) == "96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec"
    assert txn.height == 2662
    assert (
        txn.version == 1
    )  # in reality it is 0, but the JSX tfchain client converts v0 transactions automatically to v1 transactions
    assert len(txn.coin_inputs) == 1
    assert str(txn.coin_inputs[0].parentid) == "c1df239aba64ca0c6a241ddf18f3dd18b75e2c650874dd4c8c7dbbb56bd73683"
    assert len(txn.coin_outputs) == 2
    assert str(txn.coin_outputs[0].value) == "1000000"
    assert (
        str(txn.coin_outputs[1].condition.unlockhash)
        == "0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2"
    )
    assert str(txn.miner_fees[0]) == "0.1"
    assert len(txn.miner_fees) == 1

    # the explorer provides us also with info that is not part of a tfchain txn,
    # the tfchain client injects this into the txn as well for easy look-up
    assert str(txn.coin_inputs[0].parent_output.value) == "89839999.3"
    assert (
        str(txn.coin_inputs[0].parent_output.condition.unlockhash)
        == "01d1c4dd242e3badf45004be9a3b86c613923c6d872bab5ec92e4f076114d4c3a15b7b43e1c00f"
    )
    assert str(txn.coin_outputs[0].id) == "90513506d1216f89e73a361b6306d8543c81aff092e376ee8d8bb9b7ea024de6"
    assert str(txn.coin_outputs[1].id) == "7daf8035a6697701aeed36b4d6fe8de6ff4bbf9fd1ba9b0933d87e260f924783"
    assert txn.unconfirmed == False
