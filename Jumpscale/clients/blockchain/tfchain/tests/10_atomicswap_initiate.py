from Jumpscale import j

import pytest

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub
from Jumpscale.clients.blockchain.tfchain.types.PrimitiveTypes import BinaryData
from Jumpscale.clients.blockchain.tfchain.types.AtomicSwap import AtomicSwapContract, AtomicSwapSecretHash


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="atomicswap_initiate")'
    """

    # create a tfchain client for devnet
    c = j.clients.tfchain.get("mytestclient", network_type="TEST")
    # or simply `c = j.tfchain.clients.mytestclient`, should the client already exist

    # (we replace internal client logic with custom logic as to ensure we can test without requiring an active network)
    explorer_client = TFChainExplorerGetClientStub()
    # add the blockchain info
    explorer_client.chain_info = '{"blockid":"5c86c987668ca47948a149413f4f004651249073eff4f144fd26b50e218705a8","difficulty":"30203","estimatedactivebs":"2365","height":16639,"maturitytimestamp":1549646167,"target":[0,2,43,120,39,20,204,42,102,32,125,110,53,77,39,71,99,124,13,223,197,154,115,42,126,62,185,120,208,177,21,190],"totalcoins":"0","arbitrarydatatotalsize":4328,"minerpayoutcount":16721,"transactioncount":17262,"coininputcount":633,"coinoutputcount":1225,"blockstakeinputcount":16639,"blockstakeoutputcount":16640,"minerfeecount":622,"arbitrarydatacount":572}'
    explorer_client.hash_add(
        "5c86c987668ca47948a149413f4f004651249073eff4f144fd26b50e218705a8",
        '{"hashtype":"blockid","block":{"minerpayoutids":["84b378d60cbdd78430b39c8eddf226119b6f28256388557dd15f0b046bf3c3ed"],"transactions":[{"id":"9aec9f849e35f0bdd14c5ea9daed20c8fbfa09f5a6771bb46ce787eb7e2b00a0","height":16639,"parent":"5c86c987668ca47948a149413f4f004651249073eff4f144fd26b50e218705a8","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"144b2b7711fda335cdae5865ab3729d641266087bc4e088d9fba806345045903","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"f09af1c62026aed18d1d8f80e5a7bd4947a6cb5b6b69097c5b10cb983f0d729662c511a4852fa63690884e2b5c600e3935e08b81aaa757d9f0eb740292ec8309"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["83aa29b3e77f703526e28fbc0d2bfcf2b66c06b665e11cb5535b9575fd0e8105"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false}],"rawblock":{"parentid":"8485f94209bf3e01ed169244ab2072ebb0d1c5dc589c95b39a3fbab3641b7a7e","timestamp":1549646257,"pobsindexes":{"BlockHeight":16638,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"transactions":[{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"144b2b7711fda335cdae5865ab3729d641266087bc4e088d9fba806345045903","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"f09af1c62026aed18d1d8f80e5a7bd4947a6cb5b6b69097c5b10cb983f0d729662c511a4852fa63690884e2b5c600e3935e08b81aaa757d9f0eb740292ec8309"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}}]},"blockid":"5c86c987668ca47948a149413f4f004651249073eff4f144fd26b50e218705a8","difficulty":"30203","estimatedactivebs":"2365","height":16639,"maturitytimestamp":1549646167,"target":[0,2,43,120,39,20,204,42,102,32,125,110,53,77,39,71,99,124,13,223,197,154,115,42,126,62,185,120,208,177,21,190],"totalcoins":"0","arbitrarydatatotalsize":4328,"minerpayoutcount":16721,"transactioncount":17262,"coininputcount":633,"coinoutputcount":1225,"blockstakeinputcount":16639,"blockstakeoutputcount":16640,"minerfeecount":622,"arbitrarydatacount":572},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}',
    )
    # add the wallet info
    explorer_client.hash_add(
        "011dcc29c37e564ef1b0ae6273bddd6fa9c5fe5443f3a18827d3e5733892f37b2439da663e1e6f",
        '{"hashtype":"unlockhash","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"4d64c4f184ef5c7267585df8bc6af8a3e9f5963903c30ff23cfdfb068cccded7","height":16623,"parent":"95caf23ce383e01bd8af5d9391123091426278716ec5eb01a986c833119511df","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"c61aebcc2555ea16ef25152966fbbdaf2e7ba6a33c75c1033249cacc6331b2e8","fulfillment":{"type":1,"data":{"publickey":"ed25519:89ba466d80af1b453a435175dbba6da7718e9cb19c64c0ed41fca3e6982e3636","signature":"3f7c30fe4bdfc37a3f483487ef7450ee63fb6d28a7e173d6b372d895f8442ce198bf3b171cfc6315d6f03a37f00675f336a91c25b179f153237330491845f00c"}}}],"coinoutputs":[{"value":"51000000000","condition":{"type":1,"data":{"unlockhash":"011dcc29c37e564ef1b0ae6273bddd6fa9c5fe5443f3a18827d3e5733892f37b2439da663e1e6f"}}},{"value":"999627999999501","condition":{"type":1,"data":{"unlockhash":"0107e83d2bd8a7aad7ab0af0c0a0f1f116fb42335f64eeeb5ed1b76bd63e62ce59a3872a7279ab"}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"999679999999501","condition":{"type":1,"data":{"unlockhash":"0107e83d2bd8a7aad7ab0af0c0a0f1f116fb42335f64eeeb5ed1b76bd63e62ce59a3872a7279ab"}},"unlockhash":"0107e83d2bd8a7aad7ab0af0c0a0f1f116fb42335f64eeeb5ed1b76bd63e62ce59a3872a7279ab"}],"coinoutputids":["243c1bb1c7dcc18a612cf1cba4ec433f25aaedbd9916b203a66b95635f9e28b2","9516f1c1cafd58e475f424931c2f2ab9d2df62fdd263d0b075b260df80284b47"],"coinoutputunlockhashes":["011dcc29c37e564ef1b0ae6273bddd6fa9c5fe5443f3a18827d3e5733892f37b2439da663e1e6f","0107e83d2bd8a7aad7ab0af0c0a0f1f116fb42335f64eeeb5ed1b76bd63e62ce59a3872a7279ab"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"multisigaddresses":null,"unconfirmed":false}',
    )
    # override internal functionality, as to use our stub client
    c._explorer_get = explorer_client.explorer_get
    c._explorer_post = explorer_client.explorer_post

    # a wallet is required to initiate an atomic swap contract
    w = c.wallets.get(
        "mytestwallet",
        seed="survey exile lab cook license sock rose squirrel noodle point they lounge oval kit tape virus loop scare water gorilla baby educate program wish",
    )
    # money is required to be available in the wallet
    assert str(w.balance.available) == "51"

    # an atomic swap contract can be created and signed without being submitted as follows:
    result = w.atomicswap.initiate(
        participator="0131cb8e9b5214096fd23c8d88795b2887fbc898aa37125a406fc4769a4f9b3c1dc423852868f6",
        amount=50,
        submit=False,
    )  # submit=True is the default
    assert not result.submitted
    assert result.transaction.is_fulfilled()
    # the contract is returned as part of the result
    assert str(result.contract.amount) == "50"
    assert (
        str(result.contract.sender) == "011dcc29c37e564ef1b0ae6273bddd6fa9c5fe5443f3a18827d3e5733892f37b2439da663e1e6f"
    )
    assert (
        str(result.contract.receiver)
        == "0131cb8e9b5214096fd23c8d88795b2887fbc898aa37125a406fc4769a4f9b3c1dc423852868f6"
    )
    assert result.contract.refund_timestamp > 1549646257
    assert result.contract.secret_hash == AtomicSwapSecretHash.from_secret(result.secret)
    # one would than use `w.transaction_sign(result.transaction)` to submit it for real

    # However, usually an atomic swap contract is initiated as follows:
    result = w.atomicswap.initiate(
        participator="0131cb8e9b5214096fd23c8d88795b2887fbc898aa37125a406fc4769a4f9b3c1dc423852868f6",
        amount=50,
        data="the beginning of it all",
    )  # data is optional
    assert result.submitted
    # the contract is returned as part of the result
    assert str(result.contract.amount) == "50"
    assert (
        str(result.contract.sender) == "011dcc29c37e564ef1b0ae6273bddd6fa9c5fe5443f3a18827d3e5733892f37b2439da663e1e6f"
    )
    assert (
        str(result.contract.receiver)
        == "0131cb8e9b5214096fd23c8d88795b2887fbc898aa37125a406fc4769a4f9b3c1dc423852868f6"
    )
    assert result.contract.refund_timestamp > 1549646257
    assert result.contract.secret_hash == AtomicSwapSecretHash.from_secret(result.secret)

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
        w.atomicswap.initiate(
            participator="0131cb8e9b5214096fd23c8d88795b2887fbc898aa37125a406fc4769a4f9b3c1dc423852868f6",
            amount=c.minimum_miner_fee - "0.000000001 TFT",
        )
