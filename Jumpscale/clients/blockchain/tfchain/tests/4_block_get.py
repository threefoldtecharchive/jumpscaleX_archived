from Jumpscale import j

import pytest

@pytest.mark.integration
def main(self):
    """
    to run:

    js_shell 'j.clients.tfchain.test(name="block_get")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.new("mytestclient", network_type="TEST")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # get a block by hash
    blockA = c.block_get('b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f')
    # getting a block by height is possible as well
    blockB = c.block_get(2662)

    for block in [blockA, blockB]:
        # the id and height is always set for a block
        assert str(block.id) == 'b69bc0a12308938cbc8207483f39df63a2295142875944d6a2db3930d5c2564f'
        assert block.height == 2662

        # the block's parentID is always set
        # if it is equal to the NilHash than this block is the genesis block
        assert str(block.parentid) == 'ce200fdb6961c11e52fe54dd5d0e838e1bf7b7cbfa0091f115f55c150a2705b9'

        # miner payouts can be looked up as well
        assert len(block.miner_payouts) == 2
        assert str(block.miner_payouts[0].value) == '10000000000'
        assert str(block.miner_payouts[0].unlockhash) == '01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336'
        assert str(block.miner_payouts[1].value) == '100000000'
        assert str(block.miner_payouts[1].unlockhash) == '01bd7048f40168df7d837fd398bcffdf2d69d992ef53bd1677570d373ba378edea8a72317cf336'

        # transactions included in this block can be get as well
        assert isinstance(block.transactions, list) and len(block.transactions) > 0
        txn = None
        for rtxn in block.transactions:
            if str(rtxn.id) == '96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec':
                txn = rtxn
                break
        assert txn is not None

        # from the transaction you can get all kind of info
        assert str(txn.id) == '96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec'
        assert txn.version == 1 # in reality it is 0, but the JSX tfchain client converts v0 transactions automatically to v1 transactions
        assert len(txn.coin_inputs) == 1
        assert str(txn.coin_inputs[0].parent_id) == 'c1df239aba64ca0c6a241ddf18f3dd18b75e2c650874dd4c8c7dbbb56bd73683'
        assert len(txn.coin_outputs) == 2
        assert str(txn.coin_outputs[0].value) == '1000000000000000'
        assert str(txn.coin_outputs[1].condition.unlockhash) == '0175c11c8124e325cdba4f6843e917ba90519e9580adde5b10de5a7cabcc3251292194c5a0e6d2'
        assert str(txn.miner_fees[0]) == '100000000'
        assert len(txn.miner_fees) == 1
        assert str(txn.miner_fees[0]) == '100000000'
        
        # the explorer provides us also with info that is not part of a tfchain txn,
        # the tfchain client injects this into the txn as well for easy look-up
        assert str(txn.coin_inputs[0].parent_output.value) == '89839999300000000'
        assert str(txn.coin_inputs[0].parent_output.condition.unlockhash) == '01d1c4dd242e3badf45004be9a3b86c613923c6d872bab5ec92e4f076114d4c3a15b7b43e1c00f'
        assert str(txn.coin_outputs[0].id) == '90513506d1216f89e73a361b6306d8543c81aff092e376ee8d8bb9b7ea024de6'
        assert str(txn.coin_outputs[1].id) == '7daf8035a6697701aeed36b4d6fe8de6ff4bbf9fd1ba9b0933d87e260f924783'
        assert txn.unconfirmed == False
