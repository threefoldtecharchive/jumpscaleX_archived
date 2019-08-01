from Jumpscale import j

import pytest

from Jumpscale.clients.blockchain.tfchain.stub.ExplorerClientStub import TFChainExplorerGetClientStub


def main(self):
    """
    to run:

    kosmos 'j.clients.tfchain.test(name="atomicswap_verify_sender")'
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
    # override internal functionality, as to use our stub client
    c._explorer_get = explorer_client.explorer_get
    c._explorer_post = explorer_client.explorer_post

    # a wallet is required to initiate an atomic swap contract
    w = c.wallets.new(
        "mytestwallet",
        seed="remain solar kangaroo welcome clean object friend later bounce strong ship lift hamster afraid you super dolphin warm emotion curve smooth kiss stem diet",
    )

    # one can verify that its transaction is sent as sender,
    # not super useful, but it does also contain an optional check to know if it is already refundable

    # verification will fail if the contract could not be found
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractNotFound):
        w.atomicswap.verify("023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890")

    # add the coin output info of the submitted atomic swap contract
    explorer_client.hash_add(
        "023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890",
        '{"hashtype":"coinoutputid","block":{"minerpayoutids":null,"transactions":null,"rawblock":{"parentid":"0000000000000000000000000000000000000000000000000000000000000000","timestamp":0,"pobsindexes":{"BlockHeight":0,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":null,"transactions":null},"blockid":"0000000000000000000000000000000000000000000000000000000000000000","difficulty":"0","estimatedactivebs":"0","height":0,"maturitytimestamp":0,"target":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"totalcoins":"0","arbitrarydatatotalsize":0,"minerpayoutcount":0,"transactioncount":0,"coininputcount":0,"coinoutputcount":0,"blockstakeinputcount":0,"blockstakeoutputcount":0,"minerfeecount":0,"arbitrarydatacount":0},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":[{"id":"4a7ac7930379675c82d0462a86e6d6f4018bdb2bdabaf49f4c177b8de19b4e7c","height":16930,"parent":"c25f345403080b8372a38f66608aa5a2287bdc61b82efe5ee6503ce85e8bcd35","rawtransaction":{"version":1,"data":{"coininputs":[{"parentid":"753aaeaa0c9e6c9f1f8da1974c83d8ca067ad536f464a2e2fc038bbd0404d084","fulfillment":{"type":1,"data":{"publickey":"ed25519:e4f55bc46b5feb37c03a0faa2d624a9ee1d0deb5059aaa9625d8b4f60f29bcab","signature":"b5081e41797f53233c727c344698400a73f2cdd364e241df915df413d3eeafb425ce9b51de3731bcbf830c399a706f4d24ae7066f947a4a36ae1b25415bcde00"}}}],"coinoutputs":[{"value":"50000000000","condition":{"type":2,"data":{"sender":"01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0","receiver":"01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c","hashedsecret":"4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba","timelock":1549736249}}}],"minerfees":["1000000000"]}},"coininputoutputs":[{"value":"51000000000","condition":{"type":1,"data":{"unlockhash":"01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0"}},"unlockhash":"01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0"}],"coinoutputids":["023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890"],"coinoutputunlockhashes":["02fb27c67c373c2f30611e0b98bf92ed6e6eb0a69b471457b282903945180cd5c5b8068731f767"],"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false}],"multisigaddresses":null,"unconfirmed":false}',
    )

    # one can verify it all manually
    contract = w.atomicswap.verify("023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890")
    assert contract.outputid == "023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890"
    assert contract.amount == "50 TFT"
    assert contract.refund_timestamp == 1549736249
    assert contract.sender == "01b73c4e869b6167abe6180ebe7a907f56e0357b4a2f65eb53d22baad84650eb62fce66ba036d0"
    assert contract.receiver == "01746b199781ea316a44183726f81e0734d93e7cefc18e9a913989821100aafa33e6eb7343fa8c"
    assert contract.secret_hash == "4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba"

    # the amount can however be verified automatically
    w.atomicswap.verify("023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890", amount=50)
    # which will fail if the amount is wrong
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractInvalid):
        w.atomicswap.verify("023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890", amount=42)

    # the secret hash can be verified as well, not so important as the sender,
    # would be more used if one is the receiver, but it is possible none the less.
    w.atomicswap.verify(
        "023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890",
        secret_hash="4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba",
    )
    # which will fail if the secret hash is wrong
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractInvalid):
        w.atomicswap.verify(
            "023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890",
            secret_hash="4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdbb",
        )

    # a minimum duration can also be defined, where the duration defines how long it takes until the
    # contract becomes refundable, 0 if already assumed to be refundable
    w.atomicswap.verify("023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890", min_refund_time="+1d")
    # which will fail if assumed wrong
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractInvalid):
        w.atomicswap.verify("023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890", min_refund_time=0)

    # if one is assumed to be the sender, it can also be verified automatically
    w.atomicswap.verify("023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890", sender=True)
    # if one assumed its position wrong, it will however fail
    with pytest.raises(j.clients.tfchain.errors.AtomicSwapContractInvalid):
        w.atomicswap.verify("023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890", receiver=True)

    # all can be verified at once of course
    w.atomicswap.verify(
        "023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890",
        amount=50,
        secret_hash="4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba",
        min_refund_time="+1d",
        sender=True,
    )

    # once the refund time has been reached, it does become refundable, and min_refund_time=0 should validate correctly
    explorer_client.hash_add(
        "5c86c987668ca47948a149413f4f004651249073eff4f144fd26b50e218705a8",
        '{"hashtype":"blockid","block":{"minerpayoutids":["84b378d60cbdd78430b39c8eddf226119b6f28256388557dd15f0b046bf3c3ed"],"transactions":[{"id":"9aec9f849e35f0bdd14c5ea9daed20c8fbfa09f5a6771bb46ce787eb7e2b00a0","height":16639,"parent":"5c86c987668ca47948a149413f4f004651249073eff4f144fd26b50e218705a8","rawtransaction":{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"144b2b7711fda335cdae5865ab3729d641266087bc4e088d9fba806345045903","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"f09af1c62026aed18d1d8f80e5a7bd4947a6cb5b6b69097c5b10cb983f0d729662c511a4852fa63690884e2b5c600e3935e08b81aaa757d9f0eb740292ec8309"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}},"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"blockstakeoutputids":["83aa29b3e77f703526e28fbc0d2bfcf2b66c06b665e11cb5535b9575fd0e8105"],"blockstakeunlockhashes":["015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"],"unconfirmed":false}],"rawblock":{"parentid":"8485f94209bf3e01ed169244ab2072ebb0d1c5dc589c95b39a3fbab3641b7a7e","timestamp":1549791703,"pobsindexes":{"BlockHeight":16638,"TransactionIndex":0,"OutputIndex":0},"minerpayouts":[{"value":"10000000000","unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}],"transactions":[{"version":1,"data":{"coininputs":null,"blockstakeinputs":[{"parentid":"144b2b7711fda335cdae5865ab3729d641266087bc4e088d9fba806345045903","fulfillment":{"type":1,"data":{"publickey":"ed25519:d285f92d6d449d9abb27f4c6cf82713cec0696d62b8c123f1627e054dc6d7780","signature":"f09af1c62026aed18d1d8f80e5a7bd4947a6cb5b6b69097c5b10cb983f0d729662c511a4852fa63690884e2b5c600e3935e08b81aaa757d9f0eb740292ec8309"}}}],"blockstakeoutputs":[{"value":"3000","condition":{"type":1,"data":{"unlockhash":"015a080a9259b9d4aaa550e2156f49b1a79a64c7ea463d810d4493e8242e6791584fbdac553e6f"}}}],"minerfees":null}}]},"blockid":"5c86c987668ca47948a149413f4f004651249073eff4f144fd26b50e218705a8","difficulty":"30203","estimatedactivebs":"2365","height":16639,"maturitytimestamp":1549646167,"target":[0,2,43,120,39,20,204,42,102,32,125,110,53,77,39,71,99,124,13,223,197,154,115,42,126,62,185,120,208,177,21,190],"totalcoins":"0","arbitrarydatatotalsize":4328,"minerpayoutcount":16721,"transactioncount":17262,"coininputcount":633,"coinoutputcount":1225,"blockstakeinputcount":16639,"blockstakeoutputcount":16640,"minerfeecount":622,"arbitrarydatacount":572},"blocks":null,"transaction":{"id":"0000000000000000000000000000000000000000000000000000000000000000","height":0,"parent":"0000000000000000000000000000000000000000000000000000000000000000","rawtransaction":{"version":0,"data":{"coininputs":[],"minerfees":null}},"coininputoutputs":null,"coinoutputids":null,"coinoutputunlockhashes":null,"blockstakeinputoutputs":null,"blockstakeoutputids":null,"blockstakeunlockhashes":null,"unconfirmed":false},"transactions":null,"multisigaddresses":null,"unconfirmed":false}',
        force=True,
    )
    # we should be able to refund at this point
    w.atomicswap.verify(
        "023b1c17a01945573933e62ca7a1297057681622aaea52c4c4e198077a263890",
        amount=50,
        secret_hash="4163d4b31a1708cd3bb95a0a8117417bdde69fd1132909f92a8ec1e3fe2ccdba",
        min_refund_time=0,
        sender=True,
    )
