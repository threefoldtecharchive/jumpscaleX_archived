from Jumpscale import j

import pytest

@pytest.mark.integration
def main(self):
    """
    to run:

    js_shell 'j.clients.tfchain.test(name="transaction_get")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.new("mytestclient", network_type="TEST")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # get a transaction
    txn = c.transaction_get('96df1e34533ffcd42ee1db995e165538edd275ba0c065ef9293ead84ff923eec')

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
