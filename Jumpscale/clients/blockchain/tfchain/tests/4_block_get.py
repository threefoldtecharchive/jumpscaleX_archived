from Jumpscale import j

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="block_get")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mytestclient", network_type="TEST")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    explorer_client.hash_add(
        "b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f",
        '{"hashtype":"blockid","block":{"minerpayoutids":["187062a96d7c55231c0cb4d582250afa4f5a92343b86d57f95dbc1cf475a890d","5666bbf019d2b510f26092913a70477e80a3b05c0665fbd872cf9c93f84f5e00"],"transactions":[{"id":"7fc3e74073f54689ae93316871df07d109778b2eac4c1ce183998ec1051cac49","height":2662,"parent":"b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f","rawtransaction":{"version":0,"data":{"coininputs":[],"blockstakeinputs":[{"parentid":"8605cf342149179e9260bef5420963c17f0e5296a2c0d95412e4a419ebd3aa46","unlocker":{"type":1,"condition":{"publickey":"ed25519:5bb0b087153c906fb0728b10d0336816cf20b51540924ed99f4093b364092880"},"fulfillment":{"signature":"3071d9657165ab844a542035089c0390f003816171bcb85ed903c1e3e32f126aacfe3ac0afe07a77e0dc4b1442487d35da7cd6d2e8c3f79199916a8bb3e2330f"}}}],"blockstakeoutputs":[{"value":"1000","unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"1000","condition":{"type":1,"data":{"unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}},"unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}],"blockstakeoutputids":["f3f362cbb194065436e9022d722788c3abed5878b0f5431fc157de8580433cde"],"blockstakeunlockhashes":["01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"],"unconfirmed":false},{"id":"96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec","height":2662,"parent":"b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f","rawtransaction":{"version":0,"data":{"coininputs":[{"parentid":"c1df239aba64ca0c6a241ddf18f3dd18b75e2c650874dd4c8c7dbbb56bd73683","unlocker":{"type":1,"condition":{"publickey":"ed25519:25b6aae78d545d64746f4a7310230e7b7bce263dcaa9dd5b3b6dd614d0f46413"},"fulfillment":{"signature":"7453f27cca1381f0cc05a6142b8d4ded5c1f84132742ba359df99ea7c17b2f304f8b9c8f3722da9ceb632fb7f526c8022c71e385bb75df9542cf94a7f3f3cc06"}}}],"coinoutputs":[{"value":"1000000000000000","unlockhash":"0199f4f21fc13ceb22da91d4b1701e67556a7c23f118bc5b1b15b132433d07b2496e093c4f4cd6"},{"value":"88839999200000000","unlockhash":"0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2"}],"minerfees":["100000000"]}},"coininputoutputs":[{"value":"89839999300000000","condition":{"type":1,"data":{"unlockhash":"01d1c4dd242e3badf45004be9a3b86c613923c6d872bab5ec92e4f076114d4c3a15b7b43e1c00f"}},"unlockhash":"01d1c4dd242e3badf45004be9a3b86c613923c6d872bab5ec92e4f076114d4c3a15b7b43e1c00f"}],"coinoutputids":["90513506d1216f89e73a361b6306d8543c81aff092e376ee8d8bb9b7ea024de6","7daf8035a6697701aeed36b4d6fe8de6ff4bbf9fd1ba9b0933d87e260f924783"],"coinoutputunlockhashes":["0199f4f21fc13ceb22da91d4b1701e67556a7c23f118bc5b1b15b132433d07b2496e093c4f4cd6","0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"rawblock":{"parentid":"ce200fdb6961c11e52fe54dd5d0e838e1bf7b7cbfa0091f115f55c150a2705b9","timestamp":1523029892,"pobsindexes":{"BlockHeight":2657,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"},{"value":"100000000","unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}],"transactions":[{"version":0,"data":{"coininputs":[],"blockstakeinputs":[{"parentid":"8605cf342149179e9260bef5420963c17f0e5296a2c0d95412e4a419ebd3aa46","unlocker":{"type":1,"condition":{"publickey":"ed25519:5bb0b087153c906fb0728b10d0336816cf20b51540924ed99f4093b364092880"},"fulfillment":{"signature":"3071d9657165ab844a542035089c0390f003816171bcb85ed903c1e3e32f126aacfe3ac0afe07a77e0dc4b1442487d35da7cd6d2e8c3f79199916a8bb3e2330f"}}}],"blockstakeoutputs":[{"value":"1000","unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}],"minerfees":null}},{"version":0,"data":{"coininputs":[{"parentid":"c1df239aba64ca0c6a241ddf18f3dd18b75e2c650874dd4c8c7dbbb56bd73683","unlocker":{"type":1,"condition":{"publickey":"ed25519:25b6aae78d545d64746f4a7310230e7b7bce263dcaa9dd5b3b6dd614d0f46413"},"fulfillment":{"signature":"7453f27cca1381f0cc05a6142b8d4ded5c1f84132742ba359df99ea7c17b2f304f8b9c8f3722da9ceb632fb7f526c8022c71e385bb75df9542cf94a7f3f3cc06"}}}],"coinoutputs":[{"value":"1000000000000000","unlockhash":"0199f4f21fc13ceb22da91d4b1701e67556a7c23f118bc5b1b15b132433d07b2496e093c4f4cd6"},{"value":"88839999200000000","unlockhash":"0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2"}],"minerfees":["100000000"]}}]},"blockid":"b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f","difficulty":"486284","estimatedactivebs":"2460","height":2662,"maturitytimestamp":1522932967,"target":[0,0,34,128,53,10,160,139,94,201,119,200,97,208,235,36,199,95,53,168,5,195,162,76,79,152,26,149,154,217,72,198],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":2676,"transactioncount":2675,"coininputcount":15,"coinoutputcount":28,"blockstakeinputcount":2662,"blockstakeoutputcount":2665,"minerfeecount":14,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}',
    )
    explorer_client.block_add(
        2662,
        '{"block":{"minerpayoutids":["187062a96d7c55231c0cb4d582250afa4f5a92343b86d57f95dbc1cf475a890d","5666bbf019d2b510f26092913a70477e80a3b05c0665fbd872cf9c93f84f5e00"],"transactions":[{"id":"7fc3e74073f54689ae93316871df07d109778b2eac4c1ce183998ec1051cac49","height":2662,"parent":"b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f","rawtransaction":{"version":0,"data":{"coininputs":[],"blockstakeinputs":[{"parentid":"8605cf342149179e9260bef5420963c17f0e5296a2c0d95412e4a419ebd3aa46","unlocker":{"type":1,"condition":{"publickey":"ed25519:5bb0b087153c906fb0728b10d0336816cf20b51540924ed99f4093b364092880"},"fulfillment":{"signature":"3071d9657165ab844a542035089c0390f003816171bcb85ed903c1e3e32f126aacfe3ac0afe07a77e0dc4b1442487d35da7cd6d2e8c3f79199916a8bb3e2330f"}}}],"blockstakeoutputs":[{"value":"1000","unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"1000","condition":{"type":1,"data":{"unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}},"unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}],"blockstakeoutputids":["f3f362cbb194065436e9022d722788c3abed5878b0f5431fc157de8580433cde"],"blockstakeunlockhashes":["01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"],"unconfirmed":false},{"id":"96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec","height":2662,"parent":"b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f","rawtransaction":{"version":0,"data":{"coininputs":[{"parentid":"c1df239aba64ca0c6a241ddf18f3dd18b75e2c650874dd4c8c7dbbb56bd73683","unlocker":{"type":1,"condition":{"publickey":"ed25519:25b6aae78d545d64746f4a7310230e7b7bce263dcaa9dd5b3b6dd614d0f46413"},"fulfillment":{"signature":"7453f27cca1381f0cc05a6142b8d4ded5c1f84132742ba359df99ea7c17b2f304f8b9c8f3722da9ceb632fb7f526c8022c71e385bb75df9542cf94a7f3f3cc06"}}}],"coinoutputs":[{"value":"1000000000000000","unlockhash":"0199f4f21fc13ceb22da91d4b1701e67556a7c23f118bc5b1b15b132433d07b2496e093c4f4cd6"},{"value":"88839999200000000","unlockhash":"0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2"}],"minerfees":["100000000"]}},"coininputoutputs":[{"value":"89839999300000000","condition":{"type":1,"data":{"unlockhash":"01d1c4dd242e3badf45004be9a3b86c613923c6d872bab5ec92e4f076114d4c3a15b7b43e1c00f"}},"unlockhash":"01d1c4dd242e3badf45004be9a3b86c613923c6d872bab5ec92e4f076114d4c3a15b7b43e1c00f"}],"coinoutputids":["90513506d1216f89e73a361b6306d8543c81aff092e376ee8d8bb9b7ea024de6","7daf8035a6697701aeed36b4d6fe8de6ff4bbf9fd1ba9b0933d87e260f924783"],"coinoutputunlockhashes":["0199f4f21fc13ceb22da91d4b1701e67556a7c23f118bc5b1b15b132433d07b2496e093c4f4cd6","0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"rawblock":{"parentid":"ce200fdb6961c11e52fe54dd5d0e838e1bf7b7cbfa0091f115f55c150a2705b9","timestamp":1523029892,"pobsindexes":{"BlockHeight":2657,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"},{"value":"100000000","unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}],"transactions":[{"version":0,"data":{"coininputs":[],"blockstakeinputs":[{"parentid":"8605cf342149179e9260bef5420963c17f0e5296a2c0d95412e4a419ebd3aa46","unlocker":{"type":1,"condition":{"publickey":"ed25519:5bb0b087153c906fb0728b10d0336816cf20b51540924ed99f4093b364092880"},"fulfillment":{"signature":"3071d9657165ab844a542035089c0390f003816171bcb85ed903c1e3e32f126aacfe3ac0afe07a77e0dc4b1442487d35da7cd6d2e8c3f79199916a8bb3e2330f"}}}],"blockstakeoutputs":[{"value":"1000","unlockhash":"01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"}],"minerfees":null}},{"version":0,"data":{"coininputs":[{"parentid":"c1df239aba64ca0c6a241ddf18f3dd18b75e2c650874dd4c8c7dbbb56bd73683","unlocker":{"type":1,"condition":{"publickey":"ed25519:25b6aae78d545d64746f4a7310230e7b7bce263dcaa9dd5b3b6dd614d0f46413"},"fulfillment":{"signature":"7453f27cca1381f0cc05a6142b8d4ded5c1f84132742ba359df99ea7c17b2f304f8b9c8f3722da9ceb632fb7f526c8022c71e385bb75df9542cf94a7f3f3cc06"}}}],"coinoutputs":[{"value":"1000000000000000","unlockhash":"0199f4f21fc13ceb22da91d4b1701e67556a7c23f118bc5b1b15b132433d07b2496e093c4f4cd6"},{"value":"88839999200000000","unlockhash":"0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2"}],"minerfees":["100000000"]}}]},"blockid":"b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f","difficulty":"486284","estimatedactivebs":"2460","height":2662,"maturitytimestamp":1522932967,"target":[0,0,34,128,53,10,160,139,94,201,119,200,97,208,235,36,199,95,53,168,5,195,162,76,79,152,26,149,154,217,72,198],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":2676,"transactioncount":2675,"coininputcount":15,"coinoutputcount":28,"blockstakeinputcount":2662,"blockstakeoutputcount":2665,"minerfeecount":14,"arbitrarydatacount":0}}',
    )
    c._explorer_get = explorer_client.explorer_get

    # get a block by hash
    blockA = c.block_get("b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f")
    # getting a block by height is possible as well
    blockB = c.block_get(2662)

    for block in [blockA, blockB]:
        # the id and height is always set for a block
        assert str(block.id) == "b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f"
        assert block.height == 2662

        # the block's parentID is always set
        # if it is equal to the NilHash than this block is the genesis block
        assert str(block.parentid) == "ce200fdb6961c11e52fe54dd5d0e838e1bf7b7cbfa0091f115f55c150a2705b9"

        # miner payouts can be looked up as well
        assert len(block.miner_payouts) == 2
        assert str(block.miner_payouts[0].value) == "10"
        assert (
            str(block.miner_payouts[0].unlockhash)
            == "01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"
        )
        assert str(block.miner_payouts[1].value) == "0.1"
        assert (
            str(block.miner_payouts[1].unlockhash)
            == "01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336"
        )

        # transactions included in this block can be get as well
        assert isinstance(block.transactions, list) and len(block.transactions) > 0
        txn = None
        for rtxn in block.transactions:
            if str(rtxn.id) == "96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec":
                txn = rtxn
                break
        assert txn is not None

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
        assert str(txn.miner_fees[0]) == "0.1"

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
